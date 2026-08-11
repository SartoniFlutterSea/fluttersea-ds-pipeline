# Componenti documentati e nodi Figma

Mappatura dei 63 componenti di `ds-cross-app` sui nodi Figma reali.

I `metadata.json` dichiarano gli identificativi dei nodi ma non il file che
li contiene, e l'identificativo da solo non basta a dedurlo: i file
condividono gli id. Qui ogni nodo e' stato cercato in tutti i file candidati.

## Esito

| | Componenti |
|---|---|
| risolti su tutte le piattaforme | 53 |
| risolti solo in parte | 1 |
| non risolti (nodi dichiarati, nessuno risponde) | 2 |
| senza nodi dichiarati nel metadata | 7 |
| ambigui (lo stesso nodo in piu' file) | 45 |

## File Figma effettivamente usati dai componenti documentati

| File | Nodi |
|---|---|
| 📱 Design System Cross App | 125 |
| 🏗️ DS B2B | 102 |

## Non risolti

Il nodo dichiarato non risponde in nessun file candidato: e' stato
spostato, cancellato, oppure vive in un file che non abbiamo.

- **Badge Default** (`badge-default`) · 8206:634938, 8206:634938
- **Notification** (`notification`) · 8206:695184, 8206:695184

## Ambigui

Lo stesso identificativo risponde in piu' file, con componenti diversi.

- **Alert** (`alert`)
  - android · `6608:11109` → «Alert / Sticky» in 📱 Design System Cross App
  - android · `6608:11109` → «Alert / Sticky» in 🏗️ DS B2B
  - ios · `6608:11109` → «Alert / Sticky» in 📱 Design System Cross App
  - ios · `6608:11109` → «Alert / Sticky» in 🏗️ DS B2B
- **Backdrop** (`backdrop`)
  - android · `6013:46706` → «backdrop» in 📱 Design System Cross App
  - android · `6013:46706` → «backdrop» in 🏗️ DS B2B
  - ios · `6013:46706` → «backdrop» in 📱 Design System Cross App
  - ios · `6013:46706` → «backdrop» in 🏗️ DS B2B
- **Bottom Sheet** (`bottom-sheet`)
  - android · `6013:45178` → «BottomSheet» in 📱 Design System Cross App
  - android · `6013:45178` → «Drawer» in 🏗️ DS B2B
  - ios · `6013:45178` → «BottomSheet» in 📱 Design System Cross App
  - ios · `6013:45178` → «Drawer» in 🏗️ DS B2B
- **Button** (`button`)
  - android · `5473:10855` → «Button» in 📱 Design System Cross App
  - android · `5473:10855` → «Button» in 🏗️ DS B2B
  - ios · `5473:10855` → «Button» in 📱 Design System Cross App
  - ios · `5473:10855` → «Button» in 🏗️ DS B2B
- **Button Group** (`button-group`)
  - android · `5782:64435` → «Button Group» in 📱 Design System Cross App
  - android · `5782:64435` → «ButtonGroup» in 🏗️ DS B2B
  - ios · `5782:64435` → «Button Group» in 📱 Design System Cross App
  - ios · `5782:64435` → «ButtonGroup» in 🏗️ DS B2B
- **Button Icon** (`button-icon`)
  - android · `5639:2256` → «Icon Button» in 📱 Design System Cross App
  - android · `5639:2256` → «Icon Button» in 🏗️ DS B2B
  - ios · `5639:2256` → «Icon Button» in 📱 Design System Cross App
  - ios · `5639:2256` → «Icon Button» in 🏗️ DS B2B
- **Button Quicklink** (`button-quicklink`)
  - android · `6573:8694` → «buttonQuicklink» in 📱 Design System Cross App
  - android · `6573:8694` → «buttonQuicklink» in 🏗️ DS B2B
  - ios · `6573:8694` → «buttonQuicklink» in 📱 Design System Cross App
  - ios · `6573:8694` → «buttonQuicklink» in 🏗️ DS B2B
- **Button Square** (`button-square`)
  - android · `6061:60035` → «Button Square Navigation» in 📱 Design System Cross App
  - android · `6061:60035` → «Button Square Navigation» in 🏗️ DS B2B
  - ios · `6061:60035` → «Button Square Navigation» in 📱 Design System Cross App
  - ios · `6061:60035` → «Button Square Navigation» in 🏗️ DS B2B
- **Card** (`card`)
  - android · `5814:96928` → «Card» in 📱 Design System Cross App
  - android · `5814:96928` → «Card» in 🏗️ DS B2B
  - ios · `5814:96928` → «Card» in 📱 Design System Cross App
  - ios · `5814:96928` → «Card» in 🏗️ DS B2B
- **Card Detail** (`card-detail`)
  - android · `6385:825` → «cardDetails» in 📱 Design System Cross App
  - android · `6385:825` → «cardDetails» in 🏗️ DS B2B
  - ios · `6385:825` → «cardDetails» in 📱 Design System Cross App
  - ios · `6385:825` → «cardDetails» in 🏗️ DS B2B
- **Card Entrypoint** (`card-entrypoint`)
  - android · `5822:205623` → «Card Entrypoint» in 📱 Design System Cross App
  - android · `5822:205623` → «Card Entrypoint» in 🏗️ DS B2B
  - ios · `5822:205623` → «Card Entrypoint» in 📱 Design System Cross App
  - ios · `5822:205623` → «Card Entrypoint» in 🏗️ DS B2B
- **Card Highlight** (`card-highlight`)
  - android · `5822:202473` → «Card Highlight» in 📱 Design System Cross App
  - android · `5822:202473` → «Card Highlight» in 🏗️ DS B2B
  - ios · `5822:202473` → «Card Highlight» in 📱 Design System Cross App
  - ios · `5822:202473` → «Card Highlight» in 🏗️ DS B2B
- **Card Informative** (`card-informative`)
  - android · `6485:3372` → «cardInformative» in 📱 Design System Cross App
  - android · `6485:3372` → «cardInformative» in 🏗️ DS B2B
  - ios · `6485:3372` → «cardInformative» in 📱 Design System Cross App
  - ios · `6485:3372` → «cardInformative» in 🏗️ DS B2B
- **Card Loyalty** (`card-loyalty`)
  - android · `5954:2850` → «Card Loyalty» in 📱 Design System Cross App
  - android · `5954:2850` → «Card Loyalty» in 🏗️ DS B2B
  - ios · `5954:2850` → «Card Loyalty» in 📱 Design System Cross App
  - ios · `5954:2850` → «Card Loyalty» in 🏗️ DS B2B
- **Card Product** (`card-product`)
  - android · `777:8189` → «Card Product» in 📱 Design System Cross App
  - android · `777:8189` → «Card Product» in 🏗️ DS B2B
  - ios · `777:8189` → «Card Product» in 📱 Design System Cross App
  - ios · `777:8189` → «Card Product» in 🏗️ DS B2B
- **Card Promo** (`card-promo`)
  - android · `5925:30226` → «Card Promo» in 📱 Design System Cross App
  - android · `5925:30226` → «Card Promo» in 🏗️ DS B2B
  - ios · `5925:30226` → «Card Promo» in 📱 Design System Cross App
  - ios · `5925:30226` → «Card Promo» in 🏗️ DS B2B
  - carouselTemplate · `5925:30781` → «Card Promo Carousel Template» in 📱 Design System Cross App
  - carouselTemplate · `5925:30781` → «Card Promo Carousel Template» in 🏗️ DS B2B
- **Checkbox** (`checkbox`)
  - android · `5830:207986` → «Checkbox» in 📱 Design System Cross App
  - android · `5830:207986` → «Checkbox» in 🏗️ DS B2B
  - ios · `5830:207986` → «Checkbox» in 📱 Design System Cross App
  - ios · `5830:207986` → «Checkbox» in 🏗️ DS B2B
- **Chip** (`chip`)
  - android · `6005:37677` → «Chip» in 📱 Design System Cross App
  - android · `6005:37677` → «Chip» in 🏗️ DS B2B
  - ios · `6005:37677` → «Chip» in 📱 Design System Cross App
  - ios · `6005:37677` → «Chip» in 🏗️ DS B2B
- **Counter** (`counter`)
  - android · `5814:100778` → «Counter» in 📱 Design System Cross App
  - android · `5814:100778` → «timer» in 🏗️ DS B2B
  - ios · `5814:100778` → «Counter» in 📱 Design System Cross App
  - ios · `5814:100778` → «timer» in 🏗️ DS B2B
- **Dropdown** (`dropdown`)
  - android · `5914:4977` → «Dropdown input» in 📱 Design System Cross App
  - android · `5914:4977` → «Dropdown input» in 🏗️ DS B2B
  - ios · `5914:4977` → «Dropdown input» in 📱 Design System Cross App
  - ios · `5914:4977` → «Dropdown input» in 🏗️ DS B2B
  - itemsList · `5848:210081` → «Dropdown items List» in 📱 Design System Cross App
  - itemsList · `5848:210081` → «device=desktop» in 🏗️ DS B2B
- **Feedback** (`feedback`)
  - android · `6067:92459` → «Feedback» in 📱 Design System Cross App
  - android · `6067:92459` → «Feedback» in 🏗️ DS B2B
  - ios · `6067:92459` → «Feedback» in 📱 Design System Cross App
  - ios · `6067:92459` → «Feedback» in 🏗️ DS B2B
- **Filter** (`filter`)
  - android · `6061:50191` → «Filters Page Template» in 📱 Design System Cross App
  - android · `6061:50191` → «Filters Page Template» in 🏗️ DS B2B
  - ios · `6061:50191` → «Filters Page Template» in 📱 Design System Cross App
  - ios · `6061:50191` → «Filters Page Template» in 🏗️ DS B2B
- **Footer** (`footer`)
  - android · `6507:24627` → «Footer / Atom» in 📱 Design System Cross App
  - android · `6507:24627` → «Footer / Atom» in 🏗️ DS B2B
  - ios · `6507:24627` → «Footer / Atom» in 📱 Design System Cross App
  - ios · `6507:24627` → «Footer / Atom» in 🏗️ DS B2B
- **Header** (`header`)
  - android · `6135:69721` → «Top Navigation» in 📱 Design System Cross App
  - android · `6135:69721` → «Top Navigation» in 🏗️ DS B2B
  - ios · `6135:69721` → «Top Navigation» in 📱 Design System Cross App
  - ios · `6135:69721` → «Top Navigation» in 🏗️ DS B2B
  - ios-liquid-glass · `6135:69721` → «Top Navigation» in 📱 Design System Cross App
  - ios-liquid-glass · `6135:69721` → «Top Navigation» in 🏗️ DS B2B
- **Heading** (`heading`)
  - android · `5822:204388` → «Heading» in 📱 Design System Cross App
  - android · `5822:204388` → «Heading» in 🏗️ DS B2B
  - ios · `5822:204388` → «Heading» in 📱 Design System Cross App
  - ios · `5822:204388` → «Heading» in 🏗️ DS B2B
- **Hero** (`hero`)
  - android · `6091:14434` → «Hero» in 📱 Design System Cross App
  - android · `6091:14434` → «Hero» in 🏗️ DS B2B
  - ios · `6091:14434` → «Hero» in 📱 Design System Cross App
  - ios · `6091:14434` → «Hero» in 🏗️ DS B2B
- **Hero Detail** (`hero-detail`)
  - android · `6157:77450` → «Hero Detail» in 📱 Design System Cross App
  - android · `6157:77450` → «Hero Detail» in 🏗️ DS B2B
  - ios · `6157:77450` → «Hero Detail» in 📱 Design System Cross App
  - ios · `6157:77450` → «Hero Detail» in 🏗️ DS B2B
- **Link** (`link`)
  - android · `5805:90661` → «Link» in 📱 Design System Cross App
  - android · `5805:90661` → «Link» in 🏗️ DS B2B
  - ios · `5805:90661` → «Link» in 📱 Design System Cross App
  - ios · `5805:90661` → «Link» in 🏗️ DS B2B
- **Listing** (`listing`)
  - android · `6564:19499` → «Listing» in 📱 Design System Cross App
  - android · `6564:19499` → «Listing» in 🏗️ DS B2B
  - ios · `6564:19499` → «Listing» in 📱 Design System Cross App
  - ios · `6564:19499` → «Listing» in 🏗️ DS B2B
- **Listing Item** (`listing-item`)
  - android · `6199:2322` → «listingItem» in 📱 Design System Cross App
  - android · `6199:2322` → «listingItem» in 🏗️ DS B2B
  - ios · `6199:2322` → «listingItem» in 📱 Design System Cross App
  - ios · `6199:2322` → «listingItem» in 🏗️ DS B2B
  - listingItemTrail · `6645:60270` → «listingItemTrail» in 📱 Design System Cross App
  - listingItemTrail · `6645:60270` → «listingItemTrail» in 🏗️ DS B2B
- **Loader** (`loader`)
  - android · `5954:5520` → «Loader Atom» in 📱 Design System Cross App
  - android · `5954:5520` → «Loader Atom» in 🏗️ DS B2B
  - ios · `5954:5520` → «Loader Atom» in 📱 Design System Cross App
  - ios · `5954:5520` → «Loader Atom» in 🏗️ DS B2B
- **Navbar** (`navbar`)
  - navBarItem · `6067:94155` → «Nav Bar Item» in 📱 Design System Cross App
  - navBarItem · `6067:94155` → «Nav Bar Item» in 🏗️ DS B2B
  - navbarNavigation · `6068:95607` → «Navbar Navigation» in 📱 Design System Cross App
  - navbarNavigation · `6068:95607` → «Navbar Navigation» in 🏗️ DS B2B
- **Page Control** (`page-control`)
  - android · `5972:2395` → «Page Control» in 📱 Design System Cross App
  - android · `5972:2395` → «pageControl» in 🏗️ DS B2B
  - ios · `5972:2395` → «Page Control» in 📱 Design System Cross App
  - ios · `5972:2395` → «pageControl» in 🏗️ DS B2B
- **Quicklink** (`quicklink`)
  - android · `6449:2172` → «quickLink» in 📱 Design System Cross App
  - android · `6449:2172` → «quickLink» in 🏗️ DS B2B
  - ios · `6449:2172` → «quickLink» in 📱 Design System Cross App
  - ios · `6449:2172` → «quickLink» in 🏗️ DS B2B
- **Quicklink Navigation** (`quicklink-navigation`)
  - android · `6280:4229` → «Quicklink navigation» in 📱 Design System Cross App
  - android · `6280:4229` → «Quicklink navigation» in 🏗️ DS B2B
  - ios · `6280:4229` → «Quicklink navigation» in 📱 Design System Cross App
  - ios · `6280:4229` → «Quicklink navigation» in 🏗️ DS B2B
- **Radio** (`radio`)
  - android · `6032:4809` → «radio» in 📱 Design System Cross App
  - android · `6032:4809` → «radio» in 🏗️ DS B2B
  - ios · `6032:4809` → «radio» in 📱 Design System Cross App
  - ios · `6032:4809` → «radio» in 🏗️ DS B2B
- **Search Bar** (`search-bar`)
  - android · `6405:3027` → «search» in 📱 Design System Cross App
  - android · `6405:3027` → «search» in 🏗️ DS B2B
  - ios · `6405:3027` → «search» in 📱 Design System Cross App
  - ios · `6405:3027` → «search» in 🏗️ DS B2B
- **Segmented Control** (`segmented-control`)
  - ios · `6064:85468` → «OS=ios» in 📱 Design System Cross App
  - ios · `6064:85468` → «Segmented Control» in 🏗️ DS B2B
- **Splash Screen** (`splash-screen`)
  - android · `1024:12852` → «Splash Screen Template» in 📱 Design System Cross App
  - android · `1024:12852` → «Splash Screen Template» in 🏗️ DS B2B
  - ios · `1024:12852` → «Splash Screen Template» in 📱 Design System Cross App
  - ios · `1024:12852` → «Splash Screen Template» in 🏗️ DS B2B
- **Square Button Group** (`square-button-group`)
  - android · `5790:4876` → «Square Button Group» in 📱 Design System Cross App
  - android · `5790:4876` → «Square Button Group» in 🏗️ DS B2B
  - ios · `5790:4876` → «Square Button Group» in 📱 Design System Cross App
  - ios · `5790:4876` → «Square Button Group» in 🏗️ DS B2B
- **Table** (`table`)
  - android · `6668:4913` → «table» in 📱 Design System Cross App
  - android · `6668:4913` → «table» in 🏗️ DS B2B
  - ios · `6668:4913` → «table» in 📱 Design System Cross App
  - ios · `6668:4913` → «table» in 🏗️ DS B2B
  - tableHeader · `6668:4222` → «tableHeader» in 📱 Design System Cross App
  - tableHeader · `6668:4222` → «tableHeader» in 🏗️ DS B2B
  - tableRow · `6669:11288` → «tableRow» in 📱 Design System Cross App
  - tableRow · `6669:11288` → «tableRow» in 🏗️ DS B2B
- **Text Field** (`text-field`)
  - android · `5966:3890` → «.textField» in 📱 Design System Cross App
  - android · `5966:3890` → «textField» in 🏗️ DS B2B
  - ios · `5966:3890` → «.textField» in 📱 Design System Cross App
  - ios · `5966:3890` → «textField» in 🏗️ DS B2B
  - inputField · `5966:3639` → «.inputText-DEPRECATED» in 📱 Design System Cross App
  - inputField · `5966:3639` → «textField/inputField» in 🏗️ DS B2B
  - additionalText · `5809:5193` → «.textField/HelperText» in 📱 Design System Cross App
  - additionalText · `5809:5193` → «textField/additionalText» in 🏗️ DS B2B
- **Text Box** (`textbox`)
  - android · `5814:93745` → «Text Box» in 📱 Design System Cross App
  - android · `5814:93745` → «Text Box» in 🏗️ DS B2B
  - ios · `5814:93745` → «Text Box» in 📱 Design System Cross App
  - ios · `5814:93745` → «Text Box» in 🏗️ DS B2B
- **Titles And Paragraphs** (`titles-and-paragraphs`)
  - android · `5805:89762` → «Title» in 📱 Design System Cross App
  - android · `5805:89762` → «Title» in 🏗️ DS B2B
  - ios · `5805:89762` → «Title» in 📱 Design System Cross App
  - ios · `5805:89762` → «Title» in 🏗️ DS B2B
  - title · `5805:89762` → «Title» in 📱 Design System Cross App
  - title · `5805:89762` → «Title» in 🏗️ DS B2B
  - paragraph · `5805:89771` → «Paragraph» in 📱 Design System Cross App
  - paragraph · `5805:89771` → «Paragraph» in 🏗️ DS B2B
- **Toggle** (`toggle`)
  - android · `168:4540` → «Toggle» in 📱 Design System Cross App
  - android · `168:4540` → «Toggle» in 🏗️ DS B2B
  - ios · `168:4540` → «Toggle» in 📱 Design System Cross App
  - ios · `168:4540` → «Toggle» in 🏗️ DS B2B
  - toggleSwitch · `154:1983` → «Toggle Switch» in 📱 Design System Cross App
  - toggleSwitch · `154:1983` → «ToggleButton» in 🏗️ DS B2B

## Tutti i componenti

- **_example** (`_example`) · 0/0 piattaforme · ⚠️ non risolto
- **Accordion** (`accordion`) · 0/0 piattaforme · ⚠️ non risolto
- **Alert** (`alert`) · 2/2 piattaforme · 📱 Design System Cross App
- **Avatar** (`avatar`) · 2/2 piattaforme · 📱 Design System Cross App
- **Back To Top Navigation** (`back-to-top-navigation`) · 1/1 piattaforme · 📱 Design System Cross App
- **Backdrop** (`backdrop`) · 2/2 piattaforme · 📱 Design System Cross App
- **Badge Default** (`badge-default`) · 0/2 piattaforme · ⚠️ non risolto
- **Badge Ribbon** (`badge-ribbon`) · 2/2 piattaforme · 📱 Design System Cross App
- **Bottom Sheet** (`bottom-sheet`) · 3/3 piattaforme · 📱 Design System Cross App
- **Button** (`button`) · 3/3 piattaforme · 📱 Design System Cross App
- **Button Group** (`button-group`) · 2/2 piattaforme · 📱 Design System Cross App
- **Button Icon** (`button-icon`) · 3/3 piattaforme · 📱 Design System Cross App
- **Button Quicklink** (`button-quicklink`) · 2/2 piattaforme · 📱 Design System Cross App
- **Button Square** (`button-square`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card** (`card`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card Detail** (`card-detail`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card Entrypoint** (`card-entrypoint`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card Highlight** (`card-highlight`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card Informative** (`card-informative`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card Loyalty** (`card-loyalty`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card Product** (`card-product`) · 2/2 piattaforme · 📱 Design System Cross App
- **Card Promo** (`card-promo`) · 3/3 piattaforme · 📱 Design System Cross App
- **Card Tutorial** (`card-tutorial`) · 0/0 piattaforme · ⚠️ non risolto
- **Checkbox** (`checkbox`) · 2/2 piattaforme · 📱 Design System Cross App
- **Chip** (`chip`) · 2/2 piattaforme · 📱 Design System Cross App
- **Chip Navigation** (`chip-navigation`) · 2/2 piattaforme · 📱 Design System Cross App
- **Circle Button Group** (`circle-button-group`) · 0/0 piattaforme · ⚠️ non risolto
- **Counter** (`counter`) · 2/2 piattaforme · 📱 Design System Cross App
- **Divider** (`divider`) · 2/2 piattaforme · 📱 Design System Cross App
- **Dropdown** (`dropdown`) · 3/3 piattaforme · 📱 Design System Cross App
- **FAB** (`fab`) · 2/4 piattaforme · 📱 Design System Cross App
- **FAQ** (`faq`) · 0/0 piattaforme · ⚠️ non risolto
- **Feedback** (`feedback`) · 2/2 piattaforme · 📱 Design System Cross App
- **Filter** (`filter`) · 2/2 piattaforme · 📱 Design System Cross App
- **Footer** (`footer`) · 2/2 piattaforme · 📱 Design System Cross App
- **Header** (`header`) · 3/3 piattaforme · 📱 Design System Cross App
- **Heading** (`heading`) · 2/2 piattaforme · 📱 Design System Cross App
- **Hero** (`hero`) · 2/2 piattaforme · 📱 Design System Cross App
- **Hero Detail** (`hero-detail`) · 2/2 piattaforme · 📱 Design System Cross App
- **Link** (`link`) · 2/2 piattaforme · 📱 Design System Cross App
- **Listing** (`listing`) · 2/2 piattaforme · 📱 Design System Cross App
- **Listing Item** (`listing-item`) · 3/3 piattaforme · 📱 Design System Cross App
- **Loader** (`loader`) · 2/2 piattaforme · 📱 Design System Cross App
- **Menu Unico** (`menu-unico`) · 2/2 piattaforme · 📱 Design System Cross App
- **Modal Feedback** (`modal-feedback`) · 0/0 piattaforme · ⚠️ non risolto
- **Navbar** (`navbar`) · 5/5 piattaforme · 🏗️ DS B2B
- **Notification** (`notification`) · 0/2 piattaforme · ⚠️ non risolto
- **Page Control** (`page-control`) · 3/3 piattaforme · 📱 Design System Cross App
- **Page Navigation** (`page-navigation`) · 2/2 piattaforme · 📱 Design System Cross App
- **Quicklink** (`quicklink`) · 2/2 piattaforme · 📱 Design System Cross App
- **Quicklink Navigation** (`quicklink-navigation`) · 2/2 piattaforme · 📱 Design System Cross App
- **Radio** (`radio`) · 3/3 piattaforme · 📱 Design System Cross App
- **Search Bar** (`search-bar`) · 2/2 piattaforme · 📱 Design System Cross App
- **Search Results Listing** (`search-results-listing`) · 0/0 piattaforme · ⚠️ non risolto
- **Segmented Control** (`segmented-control`) · 3/3 piattaforme · 📱 Design System Cross App
- **Splash Screen** (`splash-screen`) · 2/2 piattaforme · 📱 Design System Cross App
- **Square Button Group** (`square-button-group`) · 2/2 piattaforme · 📱 Design System Cross App
- **Tab Navigation** (`tab-navigation`) · 2/2 piattaforme · 📱 Design System Cross App
- **Table** (`table`) · 4/4 piattaforme · 📱 Design System Cross App
- **Text Field** (`text-field`) · 4/4 piattaforme · 📱 Design System Cross App
- **Text Box** (`textbox`) · 2/2 piattaforme · 📱 Design System Cross App
- **Titles And Paragraphs** (`titles-and-paragraphs`) · 4/4 piattaforme · 📱 Design System Cross App
- **Toggle** (`toggle`) · 3/3 piattaforme · 📱 Design System Cross App
