#include "Localization.h"

#include <Windows.h>

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <string>
#include <string_view>
#include <unordered_map>

namespace {
    using Dictionary = std::unordered_map<std::string, std::string>;

    Dictionary g_dictionary;
    bool       g_loaded = false;

    std::string Narrow(const std::filesystem::path& a_path) {
        const auto utf8 = a_path.u8string();
        return std::string(reinterpret_cast<const char*>(utf8.data()), utf8.size());
    }

    // Where this DLL actually sits. A mod manager gives every mod its own Data
    // folder in view, and only the module handle knows which one was used.
    std::filesystem::path ModulePath() {
        HMODULE module = nullptr;
        if (!::GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                                      GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                  reinterpret_cast<LPCWSTR>(&ModulePath), &module))
            return {};

        std::wstring buffer(MAX_PATH, L'\0');

        for (;;) {
            const auto written =
                ::GetModuleFileNameW(module, buffer.data(), static_cast<DWORD>(buffer.size()));

            if (written == 0) return {};

            if (static_cast<std::size_t>(written) < buffer.size()) {
                buffer.resize(written);
                break;
            }

            buffer.resize(buffer.size() * 2);
        }

        return std::filesystem::path(buffer);
    }

    constexpr bool IsSpace(char a_character) {
        return a_character == ' ' || a_character == '\t' || a_character == '\r' ||
               a_character == '\n';
    }

    constexpr int HexValue(char a_character) {
        if (a_character >= '0' && a_character <= '9') return a_character - '0';
        if (a_character >= 'a' && a_character <= 'f') return a_character - 'a' + 10;
        if (a_character >= 'A' && a_character <= 'F') return a_character - 'A' + 10;
        return -1;
    }

    void AppendUtf8(std::string& a_out, std::uint32_t a_code) {
        if (a_code < 0x80) {
            a_out += static_cast<char>(a_code);
        } else if (a_code < 0x800) {
            a_out += static_cast<char>(0xC0 | (a_code >> 6));
            a_out += static_cast<char>(0x80 | (a_code & 0x3F));
        } else if (a_code < 0x10000) {
            a_out += static_cast<char>(0xE0 | (a_code >> 12));
            a_out += static_cast<char>(0x80 | ((a_code >> 6) & 0x3F));
            a_out += static_cast<char>(0x80 | (a_code & 0x3F));
        } else {
            a_out += static_cast<char>(0xF0 | (a_code >> 18));
            a_out += static_cast<char>(0x80 | ((a_code >> 12) & 0x3F));
            a_out += static_cast<char>(0x80 | ((a_code >> 6) & 0x3F));
            a_out += static_cast<char>(0x80 | (a_code & 0x3F));
        }
    }

    // Enough JSON for a flat object of strings. A nested value is stepped over
    // rather than rejected, so one malformed entry costs its own key and not
    // the whole file.
    class ObjectReader {
    public:
        explicit ObjectReader(std::string_view a_text) : _text(a_text) {}

        bool ReadInto(Dictionary& a_out) {
            SkipSpace();
            if (!Take('{')) return false;
            SkipSpace();

            if (Take('}')) return true;

            for (;;) {
                SkipSpace();

                std::string key;
                if (!ReadString(key)) return false;

                SkipSpace();
                if (!Take(':')) return false;

                SkipSpace();

                if (Peek() == '"') {
                    std::string value;
                    if (!ReadString(value)) return false;
                    if (!key.empty()) a_out.insert_or_assign(std::move(key), std::move(value));
                } else if (!SkipValue()) {
                    return false;
                }

                SkipSpace();
                if (Take('}')) return true;
                if (!Take(',')) return false;
            }
        }

    private:
        char Peek() const { return _pos < _text.size() ? _text[_pos] : '\0'; }

        bool Take(char a_character) {
            if (Peek() != a_character) return false;
            ++_pos;
            return true;
        }

        void SkipSpace() {
            while (_pos < _text.size() && IsSpace(_text[_pos])) ++_pos;
        }

        bool ReadString(std::string& a_out) {
            if (!Take('"')) return false;

            while (_pos < _text.size()) {
                const auto character = _text[_pos++];

                if (character == '"') return true;

                if (character != '\\') {
                    a_out += character;
                    continue;
                }

                if (_pos >= _text.size()) return false;

                switch (_text[_pos++]) {
                    case '"': a_out += '"'; break;
                    case '\\': a_out += '\\'; break;
                    case '/': a_out += '/'; break;
                    case 'b': a_out += '\b'; break;
                    case 'f': a_out += '\f'; break;
                    case 'n': a_out += '\n'; break;
                    case 'r': a_out += '\r'; break;
                    case 't': a_out += '\t'; break;
                    case 'u': {
                        std::uint32_t code = 0;
                        if (!ReadHex4(code)) return false;

                        // A character outside the BMP arrives as a surrogate
                        // pair; the low half is part of the same character.
                        if (code >= 0xD800 && code <= 0xDBFF && _pos + 1 < _text.size() &&
                            _text[_pos] == '\\' && _text[_pos + 1] == 'u') {
                            _pos += 2;

                            std::uint32_t low = 0;
                            if (!ReadHex4(low)) return false;

                            if (low >= 0xDC00 && low <= 0xDFFF)
                                code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00);
                        }

                        AppendUtf8(a_out, code);
                        break;
                    }
                    default: return false;
                }
            }

            return false;
        }

        bool ReadHex4(std::uint32_t& a_code) {
            if (_pos + 4 > _text.size()) return false;

            a_code = 0;

            for (int i = 0; i < 4; ++i) {
                const auto digit = HexValue(_text[_pos++]);
                if (digit < 0) return false;
                a_code = (a_code << 4) | static_cast<std::uint32_t>(digit);
            }

            return true;
        }

        // Steps over a value the file had no reason to carry: a nested object,
        // an array, a number, true/false/null.
        bool SkipValue() {
            SkipSpace();

            if (Peek() == '"') {
                std::string ignored;
                return ReadString(ignored);
            }

            if (Peek() == '{' || Peek() == '[') {
                const auto open  = Peek();
                const auto close = open == '{' ? '}' : ']';
                int        depth = 0;

                while (_pos < _text.size()) {
                    if (_text[_pos] == '"') {
                        std::string ignored;
                        if (!ReadString(ignored)) return false;
                        continue;
                    }

                    const auto character = _text[_pos++];

                    if (character == open)
                        ++depth;
                    else if (character == close && --depth == 0)
                        return true;
                }

                return false;
            }

            const auto start = _pos;

            while (_pos < _text.size() && !IsSpace(_text[_pos]) && _text[_pos] != ',' &&
                   _text[_pos] != '}' && _text[_pos] != ']')
                ++_pos;

            return _pos > start;
        }

        std::string_view _text;
        std::size_t      _pos = 0;
    };
}

void Localization::Load() {
    if (g_loaded) return;
    g_loaded = true;

    const auto dll = ModulePath();
    if (dll.empty()) {
        SKSE::log::warn("Can't tell which folder the plugin was loaded from, translations are off");
        return;
    }

    auto path = dll;
    path.replace_extension(L".json");

    std::ifstream file(path, std::ios::binary);
    if (!file) {
        SKSE::log::info("No translation file, English strings are used: {}", Narrow(path));
        return;
    }

    std::string text{std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>()};

    // An editor on Windows likes to leave one behind, and JSON calls it a
    // syntax error.
    if (text.size() >= 3 && static_cast<unsigned char>(text[0]) == 0xEF &&
        static_cast<unsigned char>(text[1]) == 0xBB && static_cast<unsigned char>(text[2]) == 0xBF)
        text.erase(0, 3);

    Dictionary parsed;

    if (!ObjectReader(text).ReadInto(parsed)) {
        SKSE::log::warn("Translation file isn't a flat JSON object, English strings are used: {}",
                        Narrow(path));
        return;
    }

    g_dictionary = std::move(parsed);
    SKSE::log::info("Read {} translations from {}", g_dictionary.size(), Narrow(path));
}

const char* Localization::Translate(const char* a_key) {
    if (!a_key || *a_key == '\0') return a_key;

    const auto entry = g_dictionary.find(a_key);
    return entry == g_dictionary.end() ? a_key : entry->second.c_str();
}
