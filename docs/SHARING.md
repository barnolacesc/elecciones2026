# Sharing and public discovery plan

## Shareable content in the MVP

The MVP can share the home page, a topic page, or a comparison of one topic and two parties. These pages use approved programme data. Each shared page must show the source coverage and update date. Do not share a generated claim before editorial approval.

Use stable URLs. A topic can use a path such as `/topics/housing/`. A comparison can use allowlisted party IDs in query parameters on that topic page. Do not put a visitor ID, answer, vote intention, tracking token, or free text in the URL. Keep the topic page as the canonical page until the team decides to generate separate comparison pages. Its social preview can describe the topic without claiming that a specific pair has been reviewed.

Each crawlable page needs a unique title, description, canonical URL, and Open Graph title, description, image, URL, and image alternative. Build the image locally from approved neutral design assets. Validate the preview after public deployment. Social previews are controlled by each platform and cannot be guaranteed.

## Share control

Place one clear Share control on home, topic, and comparison views. Do not repeat it after every paragraph. On supported HTTPS mobile browsers, call the [Web Share API](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share) after a user gesture. The system share sheet selects available apps. If it is unavailable or the user cancels, provide a copy-link fallback. Add a tested WhatsApp link only if it improves use. Do not promise direct posting to Instagram or TikTok from a website: the native share sheet may list an app, but support depends on the device and the installed app.

Use neutral Spanish copy, for example: “Compara las propuestas sobre vivienda y consulta los programas originales.” Do not write “Vote for…” or a claim that the site changed anyone's vote.

## Reflection prompt

The question “¿Ha cambiado tu intención de voto?” asks for a political preference signal. It is not needed for link sharing and is out of the MVP. Do not collect, store, transmit, or put its answer in a shared URL. A later quiz may offer an optional, generic, locally generated share message such as “He comparado programas sobre vivienda. ¿Quieres ver las fuentes?” It must not expose an individual result unless the user deliberately chooses that after a privacy review.

## Verification

Test iOS Safari and Android Chrome on real devices. Check the share sheet, copy-link fallback, accessible label, URL restoration, canonical metadata, social previews, and crawlability. Verify that shared links work with JavaScript off for source/context content and with JavaScript on for selection state. The domain is not chosen yet; do not claim that public sharing has been tested.

References: [Web Share API](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share), [Open Graph protocol](https://ogp.me/), [Google crawlable links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable).
