import './LegalPage.css'

function Datenschutz() {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Datenschutzerklärung</h1>
        <p className="last-updated">Stand: {new Date().toLocaleDateString('de-DE')}</p>

        <section>
          <h2>1. Datenschutz auf einen Blick</h2>
          <h3>Allgemeine Hinweise</h3>
          <p>
            Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert,
            wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit denen Sie persönlich identifiziert
            werden können.
          </p>
        </section>

        <section>
          <h2>2. Datenerfassung auf dieser Website</h2>
          <h3>Wer ist verantwortlich für die Datenerfassung auf dieser Website?</h3>
          <p>
            Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. Dessen Kontaktdaten können Sie
            dem <a href="/impressum">Impressum</a> dieser Website entnehmen.
          </p>

          <h3>Wie erfassen wir Ihre Daten?</h3>
          <p>
            Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen. Hierbei kann es sich z.B. um
            Wallet-Adressen handeln, die Sie in ein Formular eingeben.
          </p>
          <p>
            Andere Daten werden automatisch oder nach Ihrer Einwilligung beim Besuch der Website durch unsere IT-Systeme
            erfasst. Das sind vor allem technische Daten (z.B. Internetbrowser, Betriebssystem oder Uhrzeit des Seitenaufrufs).
          </p>

          <h3>Wofür nutzen wir Ihre Daten?</h3>
          <p>
            Ein Teil der Daten wird erhoben, um eine fehlerfreie Bereitstellung der Website zu gewährleisten.
            Andere Daten können zur Analyse Ihres Nutzerverhaltens verwendet werden (nur mit Ihrer Einwilligung).
          </p>

          <h3>Welche Rechte haben Sie bezüglich Ihrer Daten?</h3>
          <p>
            Sie haben jederzeit das Recht, unentgeltlich Auskunft über Herkunft, Empfänger und Zweck Ihrer gespeicherten
            personenbezogenen Daten zu erhalten. Sie haben außerdem ein Recht, die Berichtigung oder Löschung dieser Daten
            zu verlangen.
          </p>
        </section>

        <section>
          <h2>3. Hosting</h2>
          <h3>Vercel (Frontend)</h3>
          <p>
            Wir hosten unsere Website bei Vercel Inc., 340 S Lemon Ave #4133, Walnut, CA 91789, USA.
          </p>
          <p>
            <strong>Verarbeitete Daten:</strong> IP-Adresse, Browser-Informationen, Zugriffszeit
            <br />
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse)
            <br />
            <strong>Auftragsverarbeitung:</strong> Wir haben einen Vertrag über Auftragsverarbeitung (AVV) mit Vercel geschlossen.
          </p>

          <h3>Railway (Backend API)</h3>
          <p>
            Unsere Backend-API wird bei Railway Corp., 548 Market St, San Francisco, CA 94104, USA gehostet.
          </p>
          <p>
            <strong>Verarbeitete Daten:</strong> Wallet-Adressen (nur zur Analyse), API-Anfragen
            <br />
            <strong>Speicherdauer:</strong> Daten werden NICHT dauerhaft gespeichert
            <br />
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO
          </p>
        </section>

        <section>
          <h2>4. Allgemeine Hinweise und Pflichtinformationen</h2>
          <h3>Datenschutz</h3>
          <p>
            Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre
            personenbezogenen Daten vertraulich und entsprechend den gesetzlichen Datenschutzvorschriften sowie dieser
            Datenschutzerklärung.
          </p>

          <h3>Hinweis zur verantwortlichen Stelle</h3>
          <p>
            Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:
          </p>
          <p className="contact-info">
            [Ihr Name/Firma]<br />
            [Straße und Hausnummer]<br />
            [PLZ und Ort]<br />
            E-Mail: [Ihre E-Mail]
          </p>

          <h3>Speicherdauer</h3>
          <p>
            Soweit innerhalb dieser Datenschutzerklärung keine speziellere Speicherdauer genannt wurde, verbleiben
            Ihre personenbezogenen Daten bei uns, bis der Zweck für die Datenverarbeitung entfällt.
          </p>

          <h3>Widerruf Ihrer Einwilligung zur Datenverarbeitung</h3>
          <p>
            Viele Datenverarbeitungsvorgänge sind nur mit Ihrer ausdrücklichen Einwilligung möglich. Sie können eine
            bereits erteilte Einwilligung jederzeit widerrufen. Die Rechtmäßigkeit der bis zum Widerruf erfolgten
            Datenverarbeitung bleibt vom Widerruf unberührt.
          </p>

          <h3>Beschwerderecht bei der zuständigen Aufsichtsbehörde</h3>
          <p>
            Im Falle von Verstößen gegen die DSGVO steht den Betroffenen ein Beschwerderecht bei einer Aufsichtsbehörde zu.
          </p>
        </section>

        <section>
          <h2>5. Datenerfassung auf dieser Website</h2>
          <h3>Cookies</h3>
          <p>
            Unsere Internetseiten verwenden so genannte „Cookies". Cookies sind kleine Datenpakete und richten auf Ihrem
            Endgerät keinen Schaden an. Sie werden entweder vorübergehend für die Dauer einer Sitzung (Session-Cookies)
            oder dauerhaft (permanente Cookies) auf Ihrem Endgerät gespeichert.
          </p>
          <p>
            <strong>Notwendige Cookies:</strong> Speicherung Ihrer Cookie-Präferenzen
            <br />
            <strong>Analyse-Cookies:</strong> Google Analytics (nur mit Einwilligung)
            <br />
            <strong>Speicherdauer:</strong> Bis zu 12 Monate
          </p>

          <h3>Server-Log-Dateien</h3>
          <p>
            Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien:
          </p>
          <ul>
            <li>Browsertyp und Browserversion</li>
            <li>Verwendetes Betriebssystem</li>
            <li>Referrer URL</li>
            <li>Hostname des zugreifenden Rechners</li>
            <li>Uhrzeit der Serveranfrage</li>
            <li>IP-Adresse</li>
          </ul>
          <p>
            Diese Daten werden nicht mit anderen Datenquellen zusammengeführt. Die Erfassung dieser Daten erfolgt auf
            Grundlage von Art. 6 Abs. 1 lit. f DSGVO.
          </p>

          <h3>Kontaktformular / Wallet-Analyse</h3>
          <p>
            Wenn Sie unser Wallet-Analyse-Tool nutzen, werden folgende Daten verarbeitet:
          </p>
          <ul>
            <li>Wallet-Adresse (zur Analyse)</li>
            <li>Zeitpunkt der Anfrage</li>
            <li>IP-Adresse (nur für Sicherheitszwecke)</li>
          </ul>
          <p>
            <strong>Wichtig:</strong> Wir speichern KEINE Wallet-Adressen dauerhaft. Die Analyse erfolgt in Echtzeit und
            Daten werden nach Beendigung der Sitzung gelöscht.
          </p>
          <p>
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)
          </p>
        </section>

        <section>
          <h2>6. Analyse-Tools und Werbung</h2>
          <h3>Google Analytics (optional)</h3>
          <p>
            Diese Website nutzt Funktionen des Webanalysedienstes Google Analytics nur mit Ihrer ausdrücklichen Einwilligung.
            Anbieter ist die Google Ireland Limited („Google"), Gordon House, Barrow Street, Dublin 4, Irland.
          </p>
          <p>
            Google Analytics verwendet „Cookies". Die durch das Cookie erzeugten Informationen über Ihre Benutzung dieser
            Website werden in der Regel an einen Server von Google in den USA übertragen und dort gespeichert.
          </p>
          <p>
            <strong>IP-Anonymisierung:</strong> Wir haben auf dieser Website die Funktion IP-Anonymisierung aktiviert.
            <br />
            <strong>Browser Plugin:</strong> Sie können die Speicherung der Cookies durch Browser-Einstellung verhindern.
            <br />
            <strong>Widerruf:</strong> Sie können Ihre Einwilligung jederzeit über die Cookie-Einstellungen widerrufen.
          </p>
        </section>

        <section>
          <h2>7. Plugins und Tools</h2>
          <h3>Externe Blockchain-APIs</h3>
          <p>
            Zur Wallet-Analyse nutzen wir externe Blockchain-APIs:
          </p>
          <ul>
            <li><strong>Etherscan API:</strong> Ethereum-Transaktionsdaten</li>
            <li><strong>Solana RPC:</strong> Solana-Blockchain-Daten</li>
            <li><strong>Bitcoin RPC:</strong> Bitcoin-Blockchain-Daten</li>
          </ul>
          <p>
            Diese Dienste erhalten die von Ihnen eingegebene Wallet-Adresse zur Analyse. Die Daten sind öffentlich auf
            der Blockchain verfügbar.
          </p>
        </section>

        <section>
          <h2>8. Ihre Rechte</h2>
          <h3>Sie haben folgende Rechte:</h3>
          <ul>
            <li><strong>Auskunftsrecht (Art. 15 DSGVO):</strong> Recht auf Auskunft über Ihre gespeicherten Daten</li>
            <li><strong>Berichtigungsrecht (Art. 16 DSGVO):</strong> Recht auf Berichtigung unrichtiger Daten</li>
            <li><strong>Löschungsrecht (Art. 17 DSGVO):</strong> Recht auf Löschung Ihrer Daten</li>
            <li><strong>Einschränkung (Art. 18 DSGVO):</strong> Recht auf Einschränkung der Verarbeitung</li>
            <li><strong>Datenübertragbarkeit (Art. 20 DSGVO):</strong> Recht auf Datenübertragbarkeit</li>
            <li><strong>Widerspruchsrecht (Art. 21 DSGVO):</strong> Recht auf Widerspruch gegen Verarbeitung</li>
          </ul>

          <h3>Kontakt für Datenschutzanfragen</h3>
          <p>
            Für Anfragen bezüglich Ihrer Daten kontaktieren Sie uns bitte unter:
            <br />
            <strong>E-Mail:</strong> privacy@cryptoguard.io
          </p>
        </section>

        <section>
          <h2>9. Zahlungsdienstleister</h2>
          <h3>Stripe (bei Nutzung kostenpflichtiger Features)</h3>
          <p>
            Für Zahlungsabwicklung nutzen wir Stripe. Anbieter ist Stripe Payments Europe Ltd., Block 4, Harcourt Centre,
            Harcourt Road, Dublin 2, Irland.
          </p>
          <p>
            <strong>Verarbeitete Daten:</strong> Zahlungsdaten, E-Mail-Adresse, Name
            <br />
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)
            <br />
            <strong>Datenschutz:</strong> <a href="https://stripe.com/de/privacy" target="_blank" rel="noopener noreferrer">Stripe Datenschutz</a>
          </p>
        </section>

        <div className="legal-footer">
          <p>
            <strong>Hinweis:</strong> Diese Datenschutzerklärung ist eine Vorlage. Bitte passen Sie die Kontaktdaten und
            spezifischen Angaben an Ihre Situation an und lassen Sie sie ggf. von einem Anwalt prüfen.
          </p>
          <p>
            Quelle: Erstellt mit Unterstützung von eRecht24 und angepasst für CryptoGuard
          </p>
        </div>
      </div>
    </div>
  )
}

export default Datenschutz
