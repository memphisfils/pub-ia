const DEFAULT_ENDPOINT = 'https://pub-ia.io/v1';

type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;

interface ApiIntentResult {
  has_intent: boolean;
  intent: string | null;
  confidence: number;
  category: string | null;
  intent_id: string | null;
}

interface ApiAdResult {
  ad_id: string;
  headline: string;
  body: string;
  cta_text: string;
  cta_url: string;
  native_text: string;
  impression_id: string;
}

type ApiErrorPayload = {
  error?: string;
  message?: string;
  [key: string]: unknown;
};

declare const module: { exports?: unknown } | undefined;

export interface PubIAConfig {
  apiKey: string;
  appId?: string;
  endpoint?: string;
  debug?: boolean;
  fetch?: FetchLike;
}

export interface IntentResult {
  hasIntent: boolean;
  intent: string | null;
  confidence: number;
  category: string | null;
  intentId: string | null;
}

export interface AdResult {
  adId: string;
  headline: string;
  body: string;
  ctaText: string;
  ctaUrl: string;
  nativeText: string;
  impressionId: string;
}

export class PubIAError extends Error {
  readonly status?: number;
  readonly details?: unknown;

  constructor(message: string, status?: number, details?: unknown) {
    super(message);
    this.name = 'PubIAError';
    this.status = status;
    this.details = details;
  }
}

function normalizeEndpoint(endpoint?: string): string {
  const rawEndpoint = endpoint?.trim();
  if (!rawEndpoint) {
    return DEFAULT_ENDPOINT;
  }

  try {
    const parsed = new URL(rawEndpoint);
    parsed.pathname = parsed.pathname === '/' ? '/v1' : parsed.pathname.replace(/\/+$/, '');
    return parsed.toString().replace(/\/+$/, '');
  } catch {
    const trimmed = rawEndpoint.replace(/\/+$/, '');
    return trimmed || '/v1';
  }
}

function buildUrl(endpoint: string, path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${endpoint}${normalizedPath}`;
}

function stripUndefined(body: Record<string, unknown>): Record<string, unknown> {
  const cleanedBody: Record<string, unknown> = {};
  Object.entries(body).forEach(([key, value]) => {
    if (value !== undefined) {
      cleanedBody[key] = value;
    }
  });
  return cleanedBody;
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json().catch(() => null);
  }

  const text = await response.text();
  return text || null;
}

function getErrorMessage(status: number, payload: unknown): string {
  if (typeof payload === 'string' && payload.trim()) {
    return payload;
  }

  if (payload && typeof payload === 'object') {
    const errorPayload = payload as ApiErrorPayload;
    if (typeof errorPayload.error === 'string' && errorPayload.error.trim()) {
      return errorPayload.error;
    }
    if (typeof errorPayload.message === 'string' && errorPayload.message.trim()) {
      return errorPayload.message;
    }
  }

  return `HTTP ${status}`;
}

function getFetchImplementation(customFetch?: FetchLike): FetchLike {
  if (customFetch) {
    return customFetch;
  }

  if (typeof globalThis.fetch === 'function') {
    return globalThis.fetch.bind(globalThis) as FetchLike;
  }

  throw new PubIAError('No fetch implementation available. Provide one via init({ fetch }) or use Node.js 18+.');
}

function mapIntentResult(result: ApiIntentResult): IntentResult {
  return {
    hasIntent: result.has_intent,
    intent: result.intent,
    confidence: result.confidence,
    category: result.category,
    intentId: result.intent_id,
  };
}

function mapAdResult(result: ApiAdResult): AdResult {
  return {
    adId: result.ad_id,
    headline: result.headline,
    body: result.body,
    ctaText: result.cta_text,
    ctaUrl: result.cta_url,
    nativeText: result.native_text,
    impressionId: result.impression_id,
  };
}

export class PubIA {
  private apiKey = '';
  private appId = '';
  private endpoint = DEFAULT_ENDPOINT;
  private debug = false;
  private fetchImplementation: FetchLike | null = null;

  init(config: PubIAConfig): void {
    const apiKey = config.apiKey?.trim();
    if (!apiKey) {
      throw new PubIAError('apiKey is required');
    }

    this.apiKey = apiKey;
    this.appId = config.appId?.trim() || '';
    this.endpoint = normalizeEndpoint(config.endpoint);
    this.debug = Boolean(config.debug);
    this.fetchImplementation = getFetchImplementation(config.fetch);

    if (this.debug) {
      console.info('[PubIA] Initialized with endpoint:', this.endpoint);
    }
  }

  private ensureInitialized(): FetchLike {
    if (!this.apiKey) {
      throw new PubIAError('PubIA SDK is not initialized. Call pubIA.init({ apiKey }) before making requests.');
    }

    if (!this.fetchImplementation) {
      this.fetchImplementation = getFetchImplementation();
    }

    return this.fetchImplementation;
  }

  private async request<T>(path: string, body: Record<string, unknown>): Promise<T | null> {
    const fetchImplementation = this.ensureInitialized();
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };

    if (this.appId) {
      headers['X-PubIA-App-Id'] = this.appId;
    }

    let response: Response;
    try {
      response = await fetchImplementation(buildUrl(this.endpoint, path), {
        method: 'POST',
        headers,
        body: JSON.stringify(stripUndefined(body)),
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown network error';
      throw new PubIAError(`Request to Pub-IA failed: ${message}`);
    }

    if (response.status === 204) {
      return null;
    }

    const payload = await parseResponseBody(response);
    if (!response.ok) {
      throw new PubIAError(getErrorMessage(response.status, payload), response.status, payload);
    }

    return payload as T;
  }

  async analyzeIntent(prompt: string, context?: string): Promise<IntentResult> {
    if (!prompt || !prompt.trim()) {
      throw new PubIAError('prompt is required');
    }

    if (this.debug) {
      console.info('[PubIA] analyzeIntent:', prompt.slice(0, 50));
    }

    const result = await this.request<ApiIntentResult>('/analyze-intent', { prompt, context });
    if (!result) {
      throw new PubIAError('Unexpected empty response from /analyze-intent');
    }

    return mapIntentResult(result);
  }

  async getAd(intentResult: IntentResult): Promise<AdResult | null> {
    if (!intentResult?.hasIntent || !intentResult.intent) {
      return null;
    }

    if (this.debug) {
      console.info('[PubIA] getAd for intent:', intentResult.intent);
    }

    const result = await this.request<ApiAdResult>('/get-ad', {
      intent: intentResult.intent,
      intent_id: intentResult.intentId,
      confidence: intentResult.confidence,
    });

    if (!result) {
      return null;
    }

    return mapAdResult(result);
  }

  async trackClick(impressionId: string): Promise<void> {
    if (!impressionId || !impressionId.trim()) {
      throw new PubIAError('impressionId is required');
    }

    const result = await this.request<{ tracked?: boolean }>('/track-click', {
      impression_id: impressionId,
    });

    if (this.debug && result?.tracked === false) {
      console.warn('[PubIA] trackClick returned tracked=false for impression:', impressionId);
    }
  }
}

export const pubIA = new PubIA();
export default pubIA;

if (typeof module !== 'undefined' && module.exports) {
  module.exports = Object.assign(pubIA, {
    default: pubIA,
    pubIA,
    PubIA,
    PubIAError,
  });
}
