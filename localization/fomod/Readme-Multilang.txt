TextureDownscaler - Multilingual (FOMOD)
============================================

A multilingual language pack for the TextureDownscaler SKSE plugin
(Nexus 187049). The in-game/im-gui menu of the plugin is translated into
8 languages; pick one during install.

Languages:
  English, Simplified Chinese (简体中文), Japanese (日本語), Korean (한국어),
  Russian (Русский), French (Français), German (Deutsch), Spanish (Español)

How to install
--------------
1. Install this FOMOD with MO2 (or another FOMOD-aware mod manager).
2. Select your language in the install step.
3. Enable the mod in your mod list; place it wherever the original
   TextureDownscaler would be loaded from.

Files installed
---------------
  SKSE\Plugins\TextureDownscaler.dll    plugin with localization support
  SKSE\Plugins\TextureDownscaler.pdb    symbols for crash logs
  SKSE\Plugins\TextureDownscaler.json   selected language (delete to revert)

Notes
-----
- The plugin's menu window title is localized too, along with every tab and
  dialog string.
- Translation files are loaded from <mod folder>\SKSE\Plugins\TextureDownscaler.json
  next to the DLL. Removing the .json reverts the menu to English at any time.
- Chinese/Japanese/Korean glyphs come from your SKSE Menu Framework primary
  font settings (shared ImGui context); the pack ships no font on purpose.
- The plugin writes its own texture rules to TextureDownscaler.ini; this pack
  does not touch it, so your saved presets keep working.
- Requires SkyrimSE 1.5.97 / AE (same as the original plugin).

License
-------
This localization is based on TextureDownscaler by RoseEden30, licensed
GPL-3.0-or-later with a modding exception. The translated binaries and
language files are redistributed under the same terms.
Source code:
  Localization build : https://github.com/zhuabaobao123/TextureDownscaler-Multilingual
  Original plugin    : https://github.com/RoseEden30/TextureDownscaler