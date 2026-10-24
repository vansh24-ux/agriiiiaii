import { useEffect, useState } from "react";
import translations from "../translations";

const languageKeys = ["english", "hindi", "punjabi", "gujarati"];

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState(localStorage.getItem("language") || "english");
  const t = translations[language] || translations.english;
  useEffect(() => { document.documentElement.lang = t.locale; document.title = t.pageTitle; }, [t.locale, t.pageTitle]);

  function chooseLanguage(nextLanguage) {
    setLanguage(nextLanguage);
    localStorage.setItem("language", nextLanguage);
  }

  function handleSubmit(event) {
    event.preventDefault();
    const name = username.trim();

    if (!name) {
      window.alert(t.enterUsername);
      return;
    }
    if (password !== "1234") {
      window.alert(t.demoPasswordError);
      return;
    }

    localStorage.setItem("username", name);
    localStorage.setItem("language", language);
    onLogin(name);
  }

  return (
    <div className="login-page">
      <div className="wind-field-layer" aria-hidden="true" />
      <section className="login-left">
        <div className="logo">
          <img className="login-brand-logo" src="/kisanweb-logo.png" alt="KisanWeb" />
          <span>{t.appName}</span>
        </div>

        <div className="hero">
          <p className="tag">{t.loginTag}</p>
          <h1>{t.loginHeadline}</h1>
          <p className="description">{t.loginDescription}</p>
          <div className="features">
            {t.loginFeatures.map((feature) => <div key={feature}>✓ {feature}</div>)}
          </div>
        </div>

        <p className="copyright">{t.copyright}</p>
      </section>

      <section className="login-right">
        <div className="login-card">
          <p className="welcome-label">{t.welcomeBack}</p>
          <h2>{t.signIn}</h2>
          <p className="subtext">{t.signInDescription}</p>

          <form onSubmit={handleSubmit}>
            <label htmlFor="username">{t.username}</label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              placeholder={t.usernamePlaceholder}
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />

            <label htmlFor="password">{t.password}</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder={t.passwordPlaceholder}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />

            <span className="language-label">{t.chooseLanguage}</span>
            <div className="language-options" role="group" aria-label={t.chooseLanguage}>
              {languageKeys.map((key) => (
                <button
                  key={key}
                  type="button"
                  className={`language-option ${language === key ? "selected" : ""}`}
                  aria-pressed={language === key}
                  onClick={() => chooseLanguage(key)}
                >
                  <span className="language-native">{t.languages[key]}</span>
                </button>
              ))}
            </div>

            <button type="submit">{t.signIn} →</button>
          </form>

          <p className="demo">{t.demoPassword}</p>
        </div>
      </section>
    </div>
  );
}





