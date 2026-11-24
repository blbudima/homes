// Locks the map page with a password (StatiCrypt), using our own lock screen.
// Usage: node encrypt.js <in.html> <out.html> <salt-config.json>
// Key: HH_PASSWORD (the password) or HH_KEY (the hashed key from the share link).
// The salt must stay the same across deploys, or saved logins and share links stop working.
const fs = require("fs");
const path = require("path");
const SR = path.join(__dirname, "node_modules/staticrypt");
const cryptoEngine = require(SR + "/lib/cryptoEngine.js");
const codec = require(SR + "/lib/codec.js");
const { buildStaticryptJS, genFile } = require(SR + "/cli/helpers.js");
const { encodeWithHashedPassword, decode } = codec.init(cryptoEngine);

(async () => {
  const [inFile, outFile, cfgFile] = process.argv.slice(2);
  const cfg = JSON.parse(fs.readFileSync(cfgFile, "utf8"));
  const salt = cfg.salt;
  if (!/^[0-9a-f]{32}$/.test(salt)) throw new Error("bad salt in " + cfgFile);
  let key = process.env.HH_KEY;
  if (!key) {
    if (!process.env.HH_PASSWORD) throw new Error("set HH_PASSWORD or HH_KEY");
    key = await cryptoEngine.hashPassword(process.env.HH_PASSWORD, salt);
  }
  const html = fs.readFileSync(inFile, "utf8");
  const msg = await encodeWithHashedPassword(html, key);
  // check it opens again with the same key before writing anything
  const back = await decode(msg, key, salt);
  if (!back.success || back.decoded !== html) throw new Error("round-trip check failed");
  genFile({
    is_remember_enabled: "true",
    js_staticrypt: buildStaticryptJS(),
    template_button: "Open the map",
    template_color_primary: "",
    template_color_secondary: "",
    template_error: "That password didn't work. Check it and try again.",
    template_instructions: "Homes we're looking at in the South Bay. Type the password to open the map.",
    template_placeholder: "",
    template_remember: "Remember me on this device",
    template_title: "Home Hunt Map",
    template_toggle_show: "Show password",
    template_toggle_hide: "Hide password",
    staticrypt_config: {
      staticryptEncryptedMsgUniqueVariableName: msg,
      isRememberEnabled: true,
      rememberDurationInDays: 0,
      staticryptSaltUniqueVariableName: salt,
    },
  }, outFile, path.join(__dirname, "lock.html"));
  if (process.env.HH_SHARE) console.log("KEY=" + key);
})().catch((e) => { console.error(e.message); process.exit(1); });
