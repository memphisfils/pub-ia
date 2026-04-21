# Pub-IA SDK for JavaScript

JavaScript/TypeScript client for the Pub-IA publisher API.

## Install

```bash
npm install pub-ia-sdk
```

## Usage

```ts
import pubIA from 'pub-ia-sdk';

pubIA.init({
  apiKey: 'pk_live_xxx',
  endpoint: 'https://pub-ia.io'
});

const intent = await pubIA.analyzeIntent('Quel laptop acheter ?');

if (intent.hasIntent) {
  const ad = await pubIA.getAd(intent);
  if (ad) {
    console.log(ad.nativeText);
    await pubIA.trackClick(ad.impressionId);
  }
}
```

## Notes

- Default API endpoint: `https://pub-ia.io/v1`
- Custom endpoints accept either an origin such as `http://localhost:8080` or a full API base such as `http://localhost:8080/v1`
- Requires a `fetch` implementation. Browsers and Node.js 18+ work out of the box.
