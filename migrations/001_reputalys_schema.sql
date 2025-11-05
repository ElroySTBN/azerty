-- ============================================================================
-- 🗄️ SCRIPT SQL COMPLET - REPUTALYS DATABASE
-- ============================================================================
-- Migration pour Supabase (PostgreSQL) avec RLS
-- Version: 1.0
-- Date: 2024
-- ============================================================================

-- Enable UUID extension (si nécessaire)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. CONVERSATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.conversations (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    username TEXT,
    first_name TEXT,
    service_type TEXT,
    quantity TEXT,
    link TEXT,
    details TEXT,
    estimated_price TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 2. MESSAGES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES public.conversations(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    sender TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. PRICING
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.pricing (
    id SERIAL PRIMARY KEY,
    service_key TEXT UNIQUE NOT NULL,
    price TEXT NOT NULL,
    currency TEXT DEFAULT 'EUR',
    name TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 4. CRYPTO_ADDRESSES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.crypto_addresses (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    network TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. MESSAGE_TEMPLATES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.message_templates (
    id SERIAL PRIMARY KEY,
    template_key TEXT UNIQUE NOT NULL,
    template_text TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. BOT_MESSAGES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.bot_messages (
    id SERIAL PRIMARY KEY,
    message_key TEXT UNIQUE NOT NULL,
    message_text TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 7. BOT_BUTTONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.bot_buttons (
    id SERIAL PRIMARY KEY,
    button_key TEXT NOT NULL,
    button_text TEXT NOT NULL,
    callback_data TEXT NOT NULL,
    row_position INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(button_key, row_position)
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_conversations_telegram_id ON public.conversations(telegram_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON public.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_telegram_id ON public.messages(telegram_id);

-- ============================================================================
-- TRIGGERS FOR updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_pricing_updated_at ON public.pricing;
CREATE TRIGGER update_pricing_updated_at 
    BEFORE UPDATE ON public.pricing
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_crypto_addresses_updated_at ON public.crypto_addresses;
CREATE TRIGGER update_crypto_addresses_updated_at 
    BEFORE UPDATE ON public.crypto_addresses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_message_templates_updated_at ON public.message_templates;
CREATE TRIGGER update_message_templates_updated_at 
    BEFORE UPDATE ON public.message_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bot_messages_updated_at ON public.bot_messages;
CREATE TRIGGER update_bot_messages_updated_at 
    BEFORE UPDATE ON public.bot_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bot_buttons_updated_at ON public.bot_buttons;
CREATE TRIGGER update_bot_buttons_updated_at 
    BEFORE UPDATE ON public.bot_buttons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pricing ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crypto_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.message_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bot_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bot_buttons ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES - Accès public (le bot gère l'authentification)
-- ============================================================================
DROP POLICY IF EXISTS "Public access" ON public.conversations;
CREATE POLICY "Public access" ON public.conversations FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public access" ON public.messages;
CREATE POLICY "Public access" ON public.messages FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public access" ON public.pricing;
CREATE POLICY "Public access" ON public.pricing FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public access" ON public.crypto_addresses;
CREATE POLICY "Public access" ON public.crypto_addresses FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public access" ON public.message_templates;
CREATE POLICY "Public access" ON public.message_templates FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public access" ON public.bot_messages;
CREATE POLICY "Public access" ON public.bot_messages FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public access" ON public.bot_buttons;
CREATE POLICY "Public access" ON public.bot_buttons FOR ALL USING (true) WITH CHECK (true);

-- ============================================================================
-- PERMISSIONS POSTGREST
-- ============================================================================
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO anon;

-- Force PostgREST to reload schema cache
NOTIFY pgrst, 'reload schema';

-- ============================================================================
-- DONNÉES PAR DÉFAUT
-- ============================================================================
-- Insérer les prix par défaut si la table est vide
INSERT INTO public.pricing (service_key, price, currency, name)
VALUES 
    ('google', '18', 'EUR', 'Avis Google'),
    ('trustpilot', '16', 'EUR', 'Trustpilot'),
    ('forum', 'Sur devis', '', 'Message Forum'),
    ('pagesjaunes', '15', 'EUR', 'Pages Jaunes'),
    ('autre_plateforme', '15', 'EUR', 'Autre plateforme'),
    ('suppression', 'Sur devis', '', 'Suppression de liens')
ON CONFLICT (service_key) DO NOTHING;

-- Insérer les templates par défaut si la table est vide
INSERT INTO public.message_templates (template_key, template_text)
VALUES 
    ('payment_crypto', $$💰 *Informations de paiement*

Veuillez effectuer le paiement à l'adresse suivante :

*Adresse crypto :* [VOTRE_ADRESSE_CRYPTO]

*Montant :* [MONTANT]
*Réseau :* [RESEAU]

Une fois le paiement effectué, vous pouvez m'envoyer :
• Une capture d'écran de la confirmation de transaction (c'est la solution la plus simple)

Ou bien, si vous êtes à l'aise avec les cryptomonnaies :
• Le hash de la transaction (cette longue suite de caractères qui confirme votre paiement)$$),
    ('payment_received', $$✅ *Paiement reçu !*

Merci pour votre paiement. Votre commande est maintenant en cours de traitement.

*Délai estimé :* 48-72h

Je vous tiendrai informé dès que la commande sera livrée. N'hésitez pas si vous avez des questions !$$),
    ('order_confirmed', $$✅ *Commande confirmée !*

Votre commande a été bien reçue et est en cours de traitement.

*Récapitulatif :*
• Service : [SERVICE]
• Quantité : [QUANTITE]
• Prix : [PRIX]

*Délai estimé :* 48-72h

Je vous tiendrai informé de l'avancement !$$),
    ('follow_up', $$👋 Bonjour,

Souhaitez-vous un point sur l'avancement de votre commande ?

N'hésitez pas si vous avez des questions !$$)
ON CONFLICT (template_key) DO NOTHING;

-- ============================================================================
-- VÉRIFICATION
-- ============================================================================
SELECT 
    tablename,
    has_table_privilege('authenticated', 'public.' || tablename, 'SELECT') as can_select,
    has_table_privilege('authenticated', 'public.' || tablename, 'INSERT') as can_insert
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'conversations', 
    'messages', 
    'pricing', 
    'crypto_addresses',
    'message_templates',
    'bot_messages',
    'bot_buttons'
)
ORDER BY tablename;

