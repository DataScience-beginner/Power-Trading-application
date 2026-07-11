export interface ChatUser {
  id: string;
  email: string;
  display_name: string;
  role: 'platform_admin' | 'client_user';
  client_id: number | null;
  portfolio_ids: number[];
}

export interface AuthToken {
  access_token: string;
  token_type: 'bearer';
  expires_at: string;
  user: ChatUser;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent: string | null;
  provider: string | null;
  model: string | null;
  evidence: Array<Record<string, unknown>>;
  confidence: number | null;
  limitations: string[];
  safety_status: string;
  token_usage: Record<string, number>;
  created_at: string;
}

export interface ChatConversation {
  id: string;
  client_id: number;
  portfolio_id: number | null;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface ChatAnswer {
  conversation_id: string;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  suggested_questions: string[];
}
