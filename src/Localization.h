#pragma once

// Translated strings live in a JSON file next to the DLL, keyed by the English
// text the plugin already uses. A key with no entry comes back unchanged, so an
// English install (or a deleted JSON) behaves exactly as it did before.
namespace Localization {
    // Reads <DLL name>.json from the folder the plugin was loaded from. Safe to
    // call once at startup; a missing or malformed file leaves English in place.
    void Load();

    // The translation for a_key, or a_key itself when there is none.
    const char* Translate(const char* a_key);
}

// Every user-facing string goes through this.
#ifdef _T
#undef _T
#endif
#define _T(text) Localization::Translate(text)
