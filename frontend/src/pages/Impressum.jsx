import './LegalPage.css'

function Impressum() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Impressum</h1>

        <section>
          <h2>Angaben gemäß § 5 TMG</h2>
          <p className="contact-info">
            <strong>⚠️ [DEIN NAME ODER FIRMENNAME HIER EINFÜGEN]</strong><br />
            [DEINE STRASSE UND HAUSNUMMER]<br />
            [DEINE PLZ UND ORT]<br />
            Deutschland
          </p>
        </section>

        <section>
          <h2>Kontakt</h2>
          <p className="contact-info">
            <strong>E-Mail:</strong> info@cryptoguard.io<br />
            <strong>Telefon:</strong> ⚠️ [DEINE TELEFONNUMMER]<br />
            <strong>Website:</strong> https://cryptoguard.io
          </p>
        </section>

        <section>
          <h2>Umsatzsteuer-ID</h2>
          <p>
            Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br />
            <strong>⚠️ DE [DEINE UST-IDNR. ODER LÖSCHE DIESEN ABSCHNITT ALS KLEINUNTERNEHMER]</strong>
          </p>
          <p className="note">
            Hinweis: Wenn Sie noch keine USt-ID haben, können Sie diese beim Bundeszentralamt für Steuern beantragen.
            Als Kleinunternehmer nach § 19 UStG kann dieser Abschnitt entfallen.
          </p>
        </section>

        <section>
          <h2>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
          <p className="contact-info">
            ⚠️ [DEIN VOLLSTÄNDIGER NAME]<br />
            [DEINE STRASSE UND HAUSNUMMER]<br />
            [DEINE PLZ UND ORT]
          </p>
        </section>

        <section>
          <h2>EU-Streitschlichtung</h2>
          <p>
            Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
            <br />
            <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">
              https://ec.europa.eu/consumers/odr/
            </a>
          </p>
          <p>
            Unsere E-Mail-Adresse finden Sie oben im Impressum.
          </p>
        </section>

        <section>
          <h2>Verbraucherstreitbeilegung / Universalschlichtungsstelle</h2>
          <p>
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
            Verbraucherschlichtungsstelle teilzunehmen.
          </p>
        </section>

        <section>
          <h2>Haftung für Inhalte</h2>
          <p>
            Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den
            allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht
            verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu
            forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
          </p>
          <p>
            Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen
            bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer
            konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir
            diese Inhalte umgehend entfernen.
          </p>
        </section>

        <section>
          <h2>Haftung für Links</h2>
          <p>
            Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben.
            Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten
            Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.
          </p>
          <p>
            Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft.
            Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar. Eine permanente inhaltliche
            Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht
            zumutbar. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.
          </p>
        </section>

        <section>
          <h2>Urheberrecht</h2>
          <p>
            Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen
            Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der
            Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.
          </p>
          <p>
            Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen Gebrauch gestattet.
            Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter
            beachtet. Insbesondere werden Inhalte Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine
            Urheberrechtsverletzung aufmerksam werden, bitten wir um einen entsprechenden Hinweis. Bei Bekanntwerden
            von Rechtsverletzungen werden wir derartige Inhalte umgehend entfernen.
          </p>
        </section>

        <section>
          <h2>Haftungsausschluss für Wallet-Analysen</h2>
          <p className="disclaimer">
            <strong>Wichtiger Hinweis:</strong> Die von CryptoGuard bereitgestellten Wallet-Analysen und Risikobewertungen
            dienen ausschließlich zu Informationszwecken und stellen keine Anlageberatung, Finanzberatung oder
            Rechtsberatung dar.
          </p>
          <p>
            Die Analysen basieren auf öffentlich verfügbaren Blockchain-Daten und automatisierten Algorithmen.
            Wir übernehmen keine Gewähr für die Richtigkeit, Vollständigkeit oder Aktualität der bereitgestellten
            Informationen.
          </p>
          <p>
            <strong>Keine Haftung für:</strong>
          </p>
          <ul>
            <li>Finanzielle Verluste aufgrund von Entscheidungen basierend auf unseren Analysen</li>
            <li>Fehlerhafte oder unvollständige Risikobewertungen</li>
            <li>Schäden durch Nutzung externer Blockchain-APIs</li>
            <li>Verzögerungen oder Ausfälle des Services</li>
          </ul>
        </section>

        <section>
          <h2>Bildnachweise</h2>
          <p>
            Emojis: Noto Color Emoji (Google), lizenziert unter Apache License 2.0<br />
            Icons: Custom SVG Graphics
          </p>
        </section>

        <div className="legal-footer">
          <p>
            <strong>⚠️ WICHTIG:</strong> Dies ist eine Vorlage! Bitte ersetzen Sie alle Platzhalter [in eckigen Klammern]
            durch Ihre echten Daten.
          </p>
          <p>
            <strong>Benötigte Informationen:</strong>
          </p>
          <ul>
            <li>Vollständiger Name (bei Einzelunternehmen) oder Firmenname (bei GmbH/UG)</li>
            <li>Vollständige Adresse (Straße, PLZ, Ort)</li>
            <li>E-Mail-Adresse & Telefonnummer</li>
            <li>USt-IdNr. (falls vorhanden)</li>
            <li>Bei GmbH/UG: Geschäftsführer, Registergericht, Handelsregisternummer</li>
          </ul>
          <p>
            Quelle: Erstellt nach den Vorgaben des Telemediengesetzes (TMG)
          </p>
        </div>
      </div>
    </div>
  )
}

export default Impressum
