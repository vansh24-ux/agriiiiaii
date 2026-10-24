import { useEffect, useState } from "react";
import translations from "../translations";
import farmerServicesText from "../farmerServicesText";
import FarmerServices from "./FarmerServices";

const locations = {
  Jalandhar: { lat: 31.326, lon: 75.5762 },
  Ludhiana: { lat: 30.901, lon: 75.8573 },
  Amritsar: { lat: 31.634, lon: 74.8723 },
  Khanna: { lat: 30.7055, lon: 76.2219 },
  Patiala: { lat: 30.3398, lon: 76.3869 },
  Ambala: { lat: 30.3782, lon: 76.7767 },
  Karnal: { lat: 29.6857, lon: 76.9905 },
  Delhi: { lat: 28.6139, lon: 77.209 },
};

const languageKeys = ["english", "hindi", "punjabi", "gujarati"];

export default function Dashboard({ username: propUsername }) {
  const username = propUsername || localStorage.getItem("username") || "User";
  const [language, setLanguage] = useState(localStorage.getItem("language") || "english");
  const [activeView, setActiveView] = useState("markets");
  const t = translations[language] || translations.english;
  const serviceText = farmerServicesText[language] || farmerServicesText.english;
  useEffect(() => { document.documentElement.lang = t.locale; document.title = t.pageTitle; }, [t.locale, t.pageTitle]);
  const displayMandi = (name) => {
    const rawName = String(name || "").trim();
    const known = Object.entries(t.mandis || {}).find(
      ([marketName]) => marketName.toLocaleLowerCase() === rawName.toLocaleLowerCase()
    );
    if (known) return known[1];

    const match = rawName.match(/^(.*?)\s+(mandi|market)$/i);
    if (!match) return rawName;

    const city = Object.keys(t.cities || {}).find(
      (cityName) => cityName.toLocaleLowerCase() === match[1].trim().toLocaleLowerCase()
    );
    if (!city) return rawName;

    const marketWord = match[2].toLocaleLowerCase() === "mandi"
      ? { english: "Mandi", hindi: "मंडी", punjabi: "ਮੰਡੀ", gujarati: "મંડી" }
      : { english: "Market", hindi: "बाज़ार", punjabi: "ਬਾਜ਼ਾਰ", gujarati: "બજાર" };
    return `${t.cities[city]} ${marketWord[language] || marketWord.english}`;
  };
  const [crop, setCrop] = useState("Wheat");
  const [selectedLocation, setSelectedLocation] = useState("Jalandhar");
  const [location, setLocation] = useState(null);
  const [quantity, setQuantity] = useState(10);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const number = (value, digits = 0) =>
    new Intl.NumberFormat(t.locale, {
      maximumFractionDigits: digits,
      minimumFractionDigits: digits,
    }).format(Number(value) || 0);

  const changeLanguage = (event) => {
    const nextLanguage = event.target.value;
    setLanguage(nextLanguage);
    localStorage.setItem("language", nextLanguage);
  };

  const findNearbyMarkets = async () => {
    setLoading(true);
    setError("");
    setMarketData(null);

    try {
      const coordinates = location || locations[selectedLocation];
      const params = new URLSearchParams({
        latitude: String(coordinates.lat),
        longitude: String(coordinates.lon),
        max_distance_km: "100",
        quantity: String(quantity),
      });
      const response = await fetch(
        "http://127.0.0.1:8000/prices/nearby/" + encodeURIComponent(crop) + "?" + params
      );
      if (!response.ok) throw new Error(t.unableMarkets);
      const data = await response.json();

      if (!data.markets || data.markets.length === 0) {
        setError(t.noMarkets);
        return;
      }
      setMarketData(data);
    } catch {
      setError(t.unableMarkets);
    } finally {
      setLoading(false);
    }
  };

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      window.alert(t.locationNotSupported);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
      },
      () => window.alert(t.unableLocation)
    );
  };

  const markets = marketData?.markets || [];
  const bestMarket = marketData?.best_market;

  return (
    <div className="dashboard">
      <div className="wind-field-layer" aria-hidden="true" />
      <header className="dashboard-header">
        <div className="brand-section">
          <img className="dashboard-brand-logo" src="/kisanweb-logo.png" alt="KisanWeb" />
          <div className="brand-text">
            
            <p>{t.subtitle}</p>
          </div>
        </div>

        <div className="user-section">
          <label className="language-switcher">
            <span className="sr-only">{t.languageLabel}</span>
            <span aria-hidden="true">🌐</span>
            <select value={language} onChange={changeLanguage} aria-label={t.languageLabel}>
              {languageKeys.map((key) => (
                <option key={key} value={key}>{t.languages[key]}</option>
              ))}
            </select>
          </label>
          <div className="user-info">
            <div className="user-icon" aria-hidden="true">👤</div>
            <span>{t.welcome}, {username}</span>
          </div>
          <button className="logout-button" onClick={() => {
            localStorage.removeItem("username");
            window.location.reload();
          }}>{t.logout}</button>
        </div>
      </header>

      <nav className="farmer-feature-nav" aria-label={t.mainNavigation}>
        {["markets", "buyers", "transport", "alerts", "fpo", "sponsors"].map((view) => (
          <button key={view} type="button" className={activeView === view ? "active" : ""} aria-current={activeView === view ? "page" : undefined} onClick={() => setActiveView(view)}>
            {view === "markets" ? t.marketsTab : serviceText[view === "sponsors" ? "sponsorTab" : `${view}Tab`]}
          </button>
        ))}
      </nav>

      {activeView === "markets" ? <main className="dashboard-content">
        <section className="welcome-card">
          <div className="welcome-icon" aria-hidden="true">🌾</div>
          <div className="welcome-content">
            <p className="small-text">{t.smartAssistant}</p>
            <h2>{t.findBestMarket}</h2>
            <p>{t.marketIntro}</p>
          </div>
        </section>

        <section className="about-section">
          <div className="about-icon" aria-hidden="true">🌱</div>
          <div className="about-content">
            <h2>{t.aboutTitle}</h2>
            <p>{t.aboutText}</p>
          </div>
        </section>

        <section className="search-card" aria-label={t.findMarkets}>
          <div className="search-field">
            <label htmlFor="crop-select">{t.crop}</label>
            <select id="crop-select" value={crop} onChange={(event) => setCrop(event.target.value)}>
              {Object.entries(t.crops).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>

          <div className="search-field">
            <label htmlFor="location-select">{t.location}</label>
            <select
              id="location-select"
              value={selectedLocation}
              onChange={(event) => {
                setSelectedLocation(event.target.value);
                setLocation(null);
              }}
            >
              {Object.keys(locations).map((city) => (
                <option key={city} value={city}>{t.cities[city] || city}</option>
              ))}
            </select>
          </div>

          <div className="search-field">
            <label htmlFor="quantity-input">{t.quantity} ({t.quintals})</label>
            <input
              id="quantity-input"
              type="number"
              min="1"
              value={quantity}
              onChange={(event) => setQuantity(Number(event.target.value))}
            />
          </div>

          <button type="button" className="location-button" onClick={useMyLocation}>
            <span aria-hidden="true">📍</span>{t.useMyLocation}
          </button>

          <button
            type="button"
            className="search-button"
            onClick={findNearbyMarkets}
            disabled={loading || quantity <= 0}
          >
            {loading ? t.findingMarkets : t.findMarkets}
            {!loading && <span className="button-arrow" aria-hidden="true">→</span>}
          </button>
        </section>

        {error && <div className="error-message" role="alert">{error}</div>}
        {loading && <div className="status-message" role="status">{t.loading}</div>}

        {!loading && marketData && markets.length > 0 && (
          <section className="results-section">
            <div className="section-heading">
              <div>
                <h2>{t.nearbyMarkets}</h2>
                <p>
                  {t.basedOn} <strong>{location ? t.yourLocation : t.cities[selectedLocation]}</strong>
                  {" · "}{t.within} 100 {t.distanceUnit}
                </p>
              </div>
            </div>

            <div className="crop-grid">
              {markets.map((market) => {
                const isBest = market.mandi === bestMarket?.mandi;
                return (
                  <article className={isBest ? "crop-card best-market-card" : "crop-card"} key={market.mandi}>
                    <div className="crop-top">
                      <span className="crop-name">{displayMandi(market.mandi)}</span>
                      {isBest && <span className="market-name">{t.bestOption}</span>}
                    </div>
                    <h3>₹{number(market.modal_price)}<small> / {t.quintals}</small></h3>
                    <div className="market-details">
                      <span>📍 {t.distance} {number(market.distance_km, 1)} {t.distanceUnit}</span>
                    </div>
                    <div className="earning-details">
                      <div><span>{t.estimatedTransport}</span><strong>₹{number(market.transport_cost)}</strong></div>
                      <div><span>{t.grossEarning}</span><strong>₹{number(market.gross_earning)}</strong></div>
                      <div className="net-earning"><span>{t.estimatedNetEarning}</span><strong>₹{number(market.net_earning)}</strong></div>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        )}

        {!loading && bestMarket && (
          <section className="comparison-card">
            <div className="card-heading">
              <h2>{t.bestSellingOption}</h2>
              <p>{t.highestEarning}</p>
            </div>
            <div className="recommendation">
              <strong>🏆 {displayMandi(bestMarket.mandi)}</strong>
              <p>{t.recommendationReason(
                displayMandi(bestMarket.mandi),
                number(bestMarket.distance_km, 1),
                number(bestMarket.net_earning)
              )}</p>
              <div className="best-summary">
                <div><span>{t.distance}</span><strong>{number(bestMarket.distance_km, 1)} {t.distanceUnit}</strong></div>
                <div><span>{t.estimatedTransport}</span><strong>₹{number(bestMarket.transport_cost)}</strong></div>
                <div><span>{t.netEarning}</span><strong>₹{number(bestMarket.net_earning)}</strong></div>
              </div>
            </div>
          </section>
        )}
      </main> : <FarmerServices view={activeView} language={language} username={username} marketData={marketData} displayMandi={displayMandi} />}

      <footer>© 2026 {t.appName} · {t.footer}</footer>
      <div className="helpline-number"><span>{t.helpline}:</span> 09513886363</div>
    </div>
  );
}














