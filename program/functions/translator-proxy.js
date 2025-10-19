// Netlify Function: Microsoft Translator Proxy
// Keeps API key private and offers detect/translate endpoints

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
};

const API_BASE = 'https://api.cognitive.microsofttranslator.com';
const API_VERSION = '3.0';

function jsonResponse(statusCode, data) {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS
    },
    body: JSON.stringify(data)
  };
}

exports.handler = async function(event) {
  // Preflight for CORS
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: CORS_HEADERS,
      body: ''
    };
  }

  const key = process.env.TRANSLATOR_TEXT_KEY || '';
  const region = process.env.TRANSLATOR_TEXT_REGION || '';

  // Health check / ping
  if (event.httpMethod === 'GET') {
    const params = event.queryStringParameters || {};
    if (params.ping) {
      return jsonResponse(200, {
        ok: true,
        configured: Boolean(key && region)
      });
    }
    return jsonResponse(200, { ok: true });
  }

  if (event.httpMethod !== 'POST') {
    return jsonResponse(405, { error: 'Method not allowed' });
  }

  let payload;
  try {
    payload = JSON.parse(event.body || '{}');
  } catch (e) {
    return jsonResponse(400, { error: 'Invalid JSON body' });
  }

  const mode = payload.mode || 'translate';
  const texts = Array.isArray(payload.texts) ? payload.texts : [];
  const to = payload.to; // e.g., 'zh-Hans' or ['zh-Hans']
  const from = payload.from; // optional

  if (!texts.length) {
    return jsonResponse(400, { error: 'Missing texts array' });
  }

  // For translate, require toLang
  if (mode === 'translate' && !to) {
    return jsonResponse(400, { error: 'Missing target language (to)' });
  }

  if (!key || !region) {
    return jsonResponse(500, {
      error: 'Translator API key or region not configured',
      hint: 'Set environment variables TRANSLATOR_TEXT_KEY and TRANSLATOR_TEXT_REGION in Netlify.'
    });
  }

  try {
    const body = texts.map(t => ({ Text: String(t) }));

    let url;
    let msResponse;

    if (mode === 'detect') {
      url = new URL(`${API_BASE}/detect`);
      url.searchParams.set('api-version', API_VERSION);

      msResponse = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Ocp-Apim-Subscription-Key': key,
          'Ocp-Apim-Subscription-Region': region,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      const result = await msResponse.json();
      if (!msResponse.ok) {
        throw new Error(result.error?.message || `Detect failed: ${msResponse.status}`);
      }

      return jsonResponse(200, {
        success: true,
        detections: result
      });
    }

    // Translate mode
    url = new URL(`${API_BASE}/translate`);
    url.searchParams.set('api-version', API_VERSION);

    // support array or string for to
    const toList = Array.isArray(to) ? to : [to];
    for (const tl of toList) {
      url.searchParams.append('to', tl);
    }
    if (from) {
      url.searchParams.set('from', from);
    }

    msResponse = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    const result = await msResponse.json();
    if (!msResponse.ok) {
      throw new Error(result.error?.message || `Translate failed: ${msResponse.status}`);
    }

    // Flatten for convenience while exposing raw
    const flat = [];
    for (const item of result) {
      const translations = item.translations || [];
      for (const tr of translations) {
        flat.push({ text: tr.text, to: tr.to });
      }
    }

    return jsonResponse(200, {
      success: true,
      translations: flat,
      raw: result
    });
  } catch (err) {
    return jsonResponse(500, {
      error: err.message || String(err)
    });
  }
};