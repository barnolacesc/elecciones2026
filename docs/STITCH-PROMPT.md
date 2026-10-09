# Google Stitch design prompt

Design a high-fidelity, mobile-first concept for a public Spanish-language site named “Elecciones 2026” (working title). The site helps people compare political party programmes for the Spanish general election on 29 November 2026. It must be nonpartisan. Every published position must point to its original programme and exact page or section. The design must never recommend a vote.

Start with a 390 CSS-px phone frame. Check 360 and 430 px too. Use one-hand navigation, readable type, touch targets of at least 44 px, no horizontal scroll, strong contrast, and short paths to source documents. A desktop layout is secondary. Use a calm civic visual style. Do not use a party logo, party color scheme, or visual ranking.

Create these screens and states:

1. **Home:** purpose, clear “Compare programmes” action, election date, coverage, last update, and links to the method and sources.
2. **Selection:** choose a topic and two parties. Make filter changes easy on a phone. Example topics: housing, education, health/social services, economy, immigration, foreign policy.
3. **Comparison:** show a short reviewed agreement/difference summary first. Then show equal-size, vertically stacked party cards. Each card shows the position, qualifications, original source link, page/section, and review date. Let users change a topic or party without losing context.
4. **Statement detail:** neutral summary, short extract only when allowed, original source, context, version, and correction history.
5. **Sources and coverage:** party list with document status: available, partial, or missing. Explain that “not found” does not mean opposition. Include an honest empty state.
6. **Method and corrections:** plain explanation of classification and review, limitations, editor/update data, and an error-report path.

Use only “Partido A” and “Partido B” with clearly fictional example text. Do not invent real party proposals or logos. Do not add a quiz, CIS polls, seat simulator, vote prediction, accounts, analytics, or a user profile to the MVP. The public interface is Spanish. Catalan and English translations may come later, but do not show a language switch yet.

Deliver a small design system (colors, type, spacing, cards, controls, source links, empty/error states), connected screen flows, and two or three alternatives for the phone comparison screen. Show the 390-px view first, then explain wider-screen adaptation. Make it possible to compare and inspect a source in under one minute.
