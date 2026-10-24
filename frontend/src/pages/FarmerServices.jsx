import { useCallback, useEffect, useState } from "react";
import translations from "../translations";
import farmerServicesText from "../farmerServicesText";

const API = "http://127.0.0.1:8000/community";

export default function FarmerServices({ view, language, username, marketData, displayMandi }) {
  const base = translations[language] || translations.english;
  const t = farmerServicesText[language] || farmerServicesText.english;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [listings, setListings] = useState([]);
  const [transportRequests, setTransportRequests] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [sponsoredOffers, setSponsoredOffers] = useState([]);
  const [fpoSummary, setFpoSummary] = useState({ open_listings: 0, available_quintals: 0, buyer_offers: 0 });
  const [selectedListing, setSelectedListing] = useState(null);
  const [buyerMode, setBuyerMode] = useState("sell");
  const [transportMode, setTransportMode] = useState("request");
  const [bidPrice, setBidPrice] = useState("");
  const [bidMessage, setBidMessage] = useState("");
  const [listingForm, setListingForm] = useState({ crop: "Wheat", quantity_quintals: "", location: "", harvest_date: "", details: "" });
  const [transportForm, setTransportForm] = useState({ crop: "Wheat", quantity_quintals: "", pickup_location: "", destination: "", pickup_date: "" });
  const [alertForm, setAlertForm] = useState({ crop: "Wheat", market: "Any nearby market", target_price: "", direction: "above" });
  const [fpoForm, setFpoForm] = useState({ organization_name: "", district: "", member_count: "" });
  const [partnerForm, setPartnerForm] = useState({ provider_name: "", service_area: "", vehicle_capacity_quintals: "" });
  const [sponsorForm, setSponsorForm] = useState({ business_name: "", offer_title: "", category: "", target_crop: "All crops", description: "" });
  const tabKey = view === "sponsors" ? "sponsorTab" : `${view}Tab`;
  const cityKeys = Object.keys(base.cities || {});
  const cropKeys = Object.keys(base.crops || {});

  const callApi = useCallback(async (path, options = {}) => {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(t.apiError);
    return body;
  }, [t.apiError]);

  const loadViewData = useCallback(async () => {
    try {
      if (view === "buyers") {
        const data = await callApi("/listings");
        setListings(data.listings || []);
      } else if (view === "transport") {
        const data = await callApi(`/transport-requests?farmer_name=${encodeURIComponent(username)}`);
        setTransportRequests(data.requests || []);
      } else if (view === "alerts") {
        const data = await callApi(`/price-alerts?farmer_name=${encodeURIComponent(username)}`);
        setAlerts(data.alerts || []);
      } else if (view === "fpo") {
        setFpoSummary(await callApi("/fpo/summary"));
      } else if (view === "sponsors") {
        const data = await callApi("/sponsored-offers");
        setSponsoredOffers(data.offers || []);
      }
    } catch {
      setError(t.apiError);
    }
  }, [callApi, view, username, t.apiError]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadViewData(); }, 0);
    return () => window.clearTimeout(timer);
  }, [loadViewData]);

  const submit = async (event, path, payload, successText, afterSubmit) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setNotice("");
    try {
      await callApi(path, { method: "POST", body: JSON.stringify(payload) });
      setNotice(successText);
      if (afterSubmit) afterSubmit();
      await loadViewData();
    } catch (requestError) {
      setError(requestError.message || t.apiError);
    } finally {
      setLoading(false);
    }
  };

  const number = (value, decimals = 0) => new Intl.NumberFormat(base.locale, { maximumFractionDigits: decimals, minimumFractionDigits: decimals }).format(Number(value) || 0);
  const marketNow = (alert) => {
    if (!marketData || String(marketData.crop).toLowerCase() !== String(alert.crop).toLowerCase()) return null;
    const market = (marketData.markets || []).find((row) => alert.market === "Any nearby market" || alert.market === row.mandi || alert.market === row.city);
    return market?.modal_price ?? null;
  };
  const isTriggered = (alert, price) => price !== null && (alert.direction === "above" ? price >= alert.target_price : price <= alert.target_price);
  const sectionTitle = view === "buyers" ? (buyerMode === "sell" ? t.sellCrop : t.buyCrop) : view === "transport" ? (transportMode === "request" ? t.requestTransportTab : t.becomePartnerTab) : view === "alerts" ? t.alertsTab : view === "fpo" ? t.fpoTab : t.sponsorTab;
  const sectionDescription = view === "buyers" ? (buyerMode === "sell" ? t.sellCropIntro : t.buyCropIntro) : view === "transport" ? (transportMode === "request" ? t.transportIntro : t.providerNotice) : view === "alerts" ? t.alertIntro : view === "fpo" ? t.fpoIntro : t.sponsorIntro;

  return (
    <main className="dashboard-content farmer-services-content">
      <section className="feature-intro-card">
        <p className="small-text">{t[tabKey]}</p>
        <h2>{sectionTitle}</h2>
        <p>{sectionDescription}</p>
      </section>

      {error && <div className="error-message" role="alert">{error}</div>}
      {notice && <div className="feature-notice" role="status">{notice}</div>}
      {loading && <div className="status-message" role="status">{base.loading}</div>}

      {view === "buyers" && <>
        <nav className="service-subnav" aria-label={t.buyerOptions}>
          <button type="button" className={buyerMode === "sell" ? "active" : ""} aria-pressed={buyerMode === "sell"} onClick={() => setBuyerMode("sell")}>{t.sellCrop}</button>
          <button type="button" className={buyerMode === "buy" ? "active" : ""} aria-pressed={buyerMode === "buy"} onClick={() => setBuyerMode("buy")}>{t.buyCrop}</button>
        </nav>
        {buyerMode === "sell" && <section className="feature-card">
          <h3>{t.listingForm}</h3>
          <form className="feature-form feature-form-grid" onSubmit={(event) => submit(event, "/listings", { ...listingForm, farmer_name: username, quantity_quintals: Number(listingForm.quantity_quintals) }, t.listingPosted, () => setListingForm({ crop: "Wheat", quantity_quintals: "", location: "", harvest_date: "", details: "" }))}>
            <label>{base.crop}<select value={listingForm.crop} onChange={(event) => setListingForm({ ...listingForm, crop: event.target.value })}>{cropKeys.map((key) => <option key={key} value={key}>{base.crops[key]}</option>)}</select></label>
            <label>{base.quantity} ({base.quintals})<input type="number" min="0.1" step="0.1" required value={listingForm.quantity_quintals} onChange={(event) => setListingForm({ ...listingForm, quantity_quintals: event.target.value })} /></label>
            <label>{base.location}<select required value={listingForm.location} onChange={(event) => setListingForm({ ...listingForm, location: event.target.value })}><option value="">{base.location}</option>{cityKeys.map((key) => <option key={key} value={base.cities[key]}>{base.cities[key]}</option>)}</select></label>
            <label>{t.harvestDate} ({t.optional})<input type="date" value={listingForm.harvest_date} onChange={(event) => setListingForm({ ...listingForm, harvest_date: event.target.value })} /></label>
            <label className="feature-form-wide">{t.details} ({t.optional})<textarea maxLength="1000" value={listingForm.details} onChange={(event) => setListingForm({ ...listingForm, details: event.target.value })} /></label>
            <button className="search-button" disabled={loading}>{t.postCrop}</button>
          </form>
        </section>}
        <section className="feature-card">
          <h3>{buyerMode === "sell" ? t.yourListings : t.openProduce}</h3>
          {!listings.some((listing) => (listing.farmer_name.toLowerCase() === username.toLowerCase()) === (buyerMode === "sell")) && <p className="feature-muted">{buyerMode === "sell" ? t.noYourListings : t.noListings}</p>}
          <div className="community-grid">{listings.filter((listing) => (listing.farmer_name.toLowerCase() === username.toLowerCase()) === (buyerMode === "sell")).map((listing) => {
            const own = listing.farmer_name.toLowerCase() === username.toLowerCase();
            return <article className="community-item" key={listing.id}>
              <div className="community-item-heading"><strong>{base.crops[listing.crop] || listing.crop}</strong><span>{number(listing.quantity_quintals, 1)} {base.quintals}</span></div>
              <p>{base.cities[listing.location] || listing.location} · {t.byFarmer}: {listing.farmer_name}</p>
              {listing.harvest_date && <p>{t.harvestDate}: {listing.harvest_date}</p>}
              {listing.details && <p>{listing.details}</p>}
              <p className="feature-muted">{listing.offers?.length || 0} {t.offerCount}</p>
              {own ? <>
                <span className="feature-chip">{t.yourListing}</span>
                {listing.offers?.map((offer) => <div className="buyer-offer-row" key={offer.id}><strong>₹{number(offer.price_per_quintal)} / {base.quintals}</strong><span>{offer.buyer_name}{offer.message ? ` · ${offer.message}` : ""}</span></div>)}
              </> : <>
                {selectedListing === listing.id ? <form className="feature-form" onSubmit={(event) => submit(event, `/listings/${listing.id}/offers`, { buyer_name: username, price_per_quintal: Number(bidPrice), message: bidMessage }, t.offerSent, () => { setSelectedListing(null); setBidPrice(""); setBidMessage(""); })}>
                  <label>{t.pricePerQuintal}<input type="number" min="1" step="1" required value={bidPrice} onChange={(event) => setBidPrice(event.target.value)} /></label>
                  <label>{t.buyerMessage}<textarea maxLength="1000" value={bidMessage} onChange={(event) => setBidMessage(event.target.value)} /></label>
                  <button className="search-button" disabled={loading}>{t.sendOffer}</button>
                </form> : <button type="button" className="outline-button" onClick={() => setSelectedListing(listing.id)}>{t.makeOffer}</button>}
              </>}
            </article>;
          })}</div>
        </section>
      </>}

      {view === "transport" && <>
        <nav className="service-subnav" aria-label={t.transportOptions}>
          <button type="button" className={transportMode === "request" ? "active" : ""} aria-pressed={transportMode === "request"} onClick={() => setTransportMode("request")}>{t.requestTransportTab}</button>
          <button type="button" className={transportMode === "partner" ? "active" : ""} aria-pressed={transportMode === "partner"} onClick={() => setTransportMode("partner")}>{t.becomePartnerTab}</button>
        </nav>
        {transportMode === "request" && <>
        <section className="feature-card">
          <h3>{t.requestQuotes}</h3>
          <form className="feature-form feature-form-grid" onSubmit={(event) => submit(event, "/transport-requests", { ...transportForm, farmer_name: username, quantity_quintals: Number(transportForm.quantity_quintals) }, t.requestSaved, () => setTransportForm({ crop: "Wheat", quantity_quintals: "", pickup_location: "", destination: "", pickup_date: "" }))}>
            <label>{base.crop}<select value={transportForm.crop} onChange={(event) => setTransportForm({ ...transportForm, crop: event.target.value })}>{cropKeys.map((key) => <option key={key} value={key}>{base.crops[key]}</option>)}</select></label>
            <label>{base.quantity} ({base.quintals})<input type="number" min="0.1" step="0.1" required value={transportForm.quantity_quintals} onChange={(event) => setTransportForm({ ...transportForm, quantity_quintals: event.target.value })} /></label>
            <label>{t.pickup}<select required value={transportForm.pickup_location} onChange={(event) => setTransportForm({ ...transportForm, pickup_location: event.target.value })}><option value="">{t.pickup}</option>{cityKeys.map((key) => <option key={key} value={base.cities[key]}>{base.cities[key]}</option>)}</select></label>
            <label>{t.destination}<select required value={transportForm.destination} onChange={(event) => setTransportForm({ ...transportForm, destination: event.target.value })}><option value="">{t.destination}</option>{cityKeys.map((key) => <option key={key} value={base.cities[key]}>{base.cities[key]}</option>)}</select></label>
            <label>{t.pickupDate} ({t.optional})<input type="date" value={transportForm.pickup_date} onChange={(event) => setTransportForm({ ...transportForm, pickup_date: event.target.value })} /></label>
            <button className="search-button" disabled={loading}>{t.requestQuotes}</button>
          </form>
        </section>
        <section className="feature-card">
          <h3>{t.yourRequests}</h3>
          {!transportRequests.length && <p className="feature-muted">{t.noTransportRequests}</p>}
          <div className="community-grid">{transportRequests.map((request) => <article className="community-item" key={request.id}><strong>{base.crops[request.crop] || request.crop} · {number(request.quantity_quintals, 1)} {base.quintals}</strong><p>{request.pickup_location} → {request.destination}</p><span className="feature-chip">{t.pending}</span></article>)}</div>
        </section>
        </>}
        {transportMode === "partner" && <section className="feature-card">
          <p className="feature-muted partner-note">{t.providerNotice}</p>
          <h3>{t.partnerApplication}</h3>
          <form className="feature-form feature-form-grid" onSubmit={(event) => submit(event, "/transport-partners/applications", { ...partnerForm, submitted_by: username, vehicle_capacity_quintals: Number(partnerForm.vehicle_capacity_quintals) }, t.partnerApplicationSent, () => setPartnerForm({ provider_name: "", service_area: "", vehicle_capacity_quintals: "" }))}>
            <label>{t.providerName}<input required maxLength="140" value={partnerForm.provider_name} onChange={(event) => setPartnerForm({ ...partnerForm, provider_name: event.target.value })} /></label>
            <label>{t.serviceArea}<input required maxLength="120" value={partnerForm.service_area} onChange={(event) => setPartnerForm({ ...partnerForm, service_area: event.target.value })} /></label>
            <label>{t.truckCapacity} ({base.quintals})<input type="number" min="0.1" step="0.1" required value={partnerForm.vehicle_capacity_quintals} onChange={(event) => setPartnerForm({ ...partnerForm, vehicle_capacity_quintals: event.target.value })} /></label>
            <button className="outline-button" disabled={loading}>{t.applyPartner}</button>
          </form>
        </section>}</>}

      {view === "alerts" && <>
        <section className="feature-card">
          <h3>{t.saveAlert}</h3>
          <form className="feature-form feature-form-grid" onSubmit={(event) => submit(event, "/price-alerts", { ...alertForm, farmer_name: username, target_price: Number(alertForm.target_price) }, t.alertSaved, () => setAlertForm({ ...alertForm, target_price: "" }))}>
            <label>{base.crop}<select value={alertForm.crop} onChange={(event) => setAlertForm({ ...alertForm, crop: event.target.value })}>{cropKeys.map((key) => <option key={key} value={key}>{base.crops[key]}</option>)}</select></label>
            <label>{t.market}<select value={alertForm.market} onChange={(event) => setAlertForm({ ...alertForm, market: event.target.value })}><option value="Any nearby market">{t.anyMarket}</option>{(marketData?.markets || []).map((market) => <option key={market.mandi} value={market.mandi}>{displayMandi(market.mandi)}</option>)}</select></label>
            <label>{t.when}<select value={alertForm.direction} onChange={(event) => setAlertForm({ ...alertForm, direction: event.target.value })}><option value="above">{t.priceAtLeast}</option><option value="below">{t.priceAtMost}</option></select></label>
            <label>{t.targetPrice}<input type="number" min="1" step="1" required value={alertForm.target_price} onChange={(event) => setAlertForm({ ...alertForm, target_price: event.target.value })} /></label>
            <button className="search-button" disabled={loading}>{t.saveAlert}</button>
          </form>
          <p className="feature-muted partner-note">{t.alertPollNote}</p>
        </section>
        <section className="feature-card">
          <h3>{t.savedAlerts}</h3>
          {!alerts.length && <p className="feature-muted">{t.noAlerts}</p>}
          <div className="community-grid">{alerts.map((alert) => {
            const currentPrice = marketNow(alert);
            const reached = isTriggered(alert, currentPrice);
            return <article className="community-item alert-item" key={alert.id}>
              <strong>{base.crops[alert.crop] || alert.crop} · {alert.direction === "above" ? t.priceAtLeast : t.priceAtMost} ₹{number(alert.target_price)}</strong>
              <p>{alert.market === "Any nearby market" ? t.anyMarket : displayMandi(alert.market)}</p>
              <span className={reached ? "feature-chip feature-chip-active" : "feature-chip"}>{currentPrice === null ? t.notTriggered : reached ? `${t.triggered} · ₹${number(currentPrice)}` : t.notTriggered}</span>
              <button type="button" className="text-button" onClick={async () => { try { await callApi(`/price-alerts/${alert.id}?farmer_name=${encodeURIComponent(username)}`, { method: "DELETE" }); await loadViewData(); } catch { setError(t.apiError); } }}>{t.remove}</button>
            </article>;
          })}</div>
        </section>
      </>}

      {view === "fpo" && <>
        <section className="community-grid stats-grid">
          <article className="stat-card"><span>{t.activeListings}</span><strong>{number(fpoSummary.open_listings)}</strong></article>
          <article className="stat-card"><span>{t.totalVolume}</span><strong>{number(fpoSummary.available_quintals, 1)}</strong></article>
          <article className="stat-card"><span>{t.buyerOffers}</span><strong>{number(fpoSummary.buyer_offers)}</strong></article>
        </section>
        <section className="feature-card">
          <h3>{t.requestDemo}</h3>
          <form className="feature-form feature-form-grid" onSubmit={(event) => submit(event, "/fpo/enquiries", { ...fpoForm, submitted_by: username, member_count: Number(fpoForm.member_count) }, t.demoRequested, () => setFpoForm({ organization_name: "", district: "", member_count: "" }))}>
            <label>{t.orgName}<input required minLength="2" maxLength="140" value={fpoForm.organization_name} onChange={(event) => setFpoForm({ ...fpoForm, organization_name: event.target.value })} /></label>
            <label>{t.district}<input required minLength="2" maxLength="120" value={fpoForm.district} onChange={(event) => setFpoForm({ ...fpoForm, district: event.target.value })} /></label>
            <label>{t.memberCount}<input type="number" min="1" step="1" required value={fpoForm.member_count} onChange={(event) => setFpoForm({ ...fpoForm, member_count: event.target.value })} /></label>
            <button className="search-button" disabled={loading}>{t.submitRequest}</button>
          </form>
        </section>
      </>}

      {view === "sponsors" && <>
        <section className="feature-card">
          <h3>{t.sponsored}</h3>
          {!sponsoredOffers.length && <p className="feature-muted">{t.noOffers}</p>}
          <div className="community-grid">{sponsoredOffers.map((offer) => <article className="community-item sponsored-item" key={offer.id}><span className="feature-chip">{t.sponsored}</span><h3>{offer.offer_title}</h3><p>{offer.business_name} · {offer.category}</p><p>{offer.target_crop === "All crops" ? t.allCrops : base.crops[offer.target_crop] || offer.target_crop}</p><p>{offer.description}</p></article>)}</div>
        </section>
        <section className="feature-card">
          <h3>{t.partnerApplication}</h3>
          <form className="feature-form feature-form-grid" onSubmit={(event) => submit(event, "/sponsored-offers/applications", { ...sponsorForm, submitted_by: username }, t.offerPending, () => setSponsorForm({ business_name: "", offer_title: "", category: "", target_crop: "All crops", description: "" }))}>
            <label>{t.business}<input required minLength="2" maxLength="140" value={sponsorForm.business_name} onChange={(event) => setSponsorForm({ ...sponsorForm, business_name: event.target.value })} /></label>
            <label>{t.offerTitle}<input required minLength="2" maxLength="140" value={sponsorForm.offer_title} onChange={(event) => setSponsorForm({ ...sponsorForm, offer_title: event.target.value })} /></label>
            <label>{t.category}<input required minLength="2" maxLength="80" value={sponsorForm.category} onChange={(event) => setSponsorForm({ ...sponsorForm, category: event.target.value })} /></label>
            <label>{t.targetCrop}<select value={sponsorForm.target_crop} onChange={(event) => setSponsorForm({ ...sponsorForm, target_crop: event.target.value })}><option value="All crops">{t.allCrops}</option>{cropKeys.map((key) => <option key={key} value={key}>{base.crops[key]}</option>)}</select></label>
            <label className="feature-form-wide">{t.description}<textarea required minLength="5" maxLength="1000" value={sponsorForm.description} onChange={(event) => setSponsorForm({ ...sponsorForm, description: event.target.value })} /></label>
            <button className="outline-button" disabled={loading}>{t.submitOffer}</button>
          </form>
        </section>
      </>}
    </main>
  );
}
