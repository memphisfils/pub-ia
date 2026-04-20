const BASE_URL = '/v1';

export interface PubIAConfig {
  apiKey: string;
  appId?: string;
  endpoint?: string;
  debug?: boolean;
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

class PubIA {
  private apiKey: string = '';
  private appId: string = '';
  private endpoint: string = BASE_URL;
  private debug: boolean = false;

  init(config: PubIAConfig): void {
    this.apiKey = config.apiKey;
    this.appId = config.appId || '';
    this.endpoint = config.endpoint || BASE_URL;
    this.debug = config.debug || false;
    if (this.debug) console.log('[PubIA] Initialized with endpoint:', this.endpoint);
  }

  private async request<T>(path: string, body: object): Promise<T> {
    const response = await fetch(`${this.endpoint}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    });
    if (response.status === 204) return null as T;
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }
    return response.json();
  }

  async analyzeIntent(prompt: string, context?: string): Promise<IntentResult> {
    if (this.debug) console.log('[PubIA] analyzeIntent:', prompt.slice(0, 50));
    const result = await this.request<{
      has_intent: boolean;
      intent: string | null;
      confidence: number;
      category: string | null;
      intent_id: string;
    }>('/analyze-intent', { prompt, context });
    return {
      hasIntent: result.has_intent,
      intent: result.intent,
      confidence: result.confidence,
      category: result.category,
      intentId: result.intent_id,
    };
  }

  async getAd(intentResult: IntentResult): Promise<AdResult | null> {
    if (!intentResult.hasIntent || !intentResult.intent) return null;
    if (this.debug) console.log('[PubIA] getAd for intent:', intentResult.intent);
    const result = await this.request<{
      ad_id: string;
      headline: string;
      body: string;
      cta_text: string;
      cta_url: string;
      native_text: string;
      impression_id: string;
    }>('/get-ad', {
      intent: intentResult.intent,
      intent_id: intentResult.intentId,
      confidence: intentResult.confidence,
    });
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

  async trackClick(impressionId: string): Promise<void> {
    await this.request('/track-click', { impression_id: impressionId });
  }
}

export const pubIA = new PubIA();
export default pubIA;
