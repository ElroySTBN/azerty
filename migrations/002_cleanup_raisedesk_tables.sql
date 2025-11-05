-- ============================================================================
-- 🧹 SCRIPT DE NETTOYAGE - SUPPRESSION DES TABLES RAISEDESK
-- ============================================================================
-- Ce script supprime toutes les tables RaiseDesk qui ne sont pas utilisées
-- par Reputalys. À exécuter dans Supabase SQL Editor après avoir vérifié
-- que vous n'avez pas besoin de ces données.
-- ============================================================================
-- ATTENTION : Cette opération est IRRÉVERSIBLE !
-- Assurez-vous d'avoir une sauvegarde si nécessaire.
-- ============================================================================

-- Supprimer les vues d'abord (car elles dépendent des tables)
DROP VIEW IF EXISTS public.contacts_with_organization CASCADE;

-- Supprimer les tables RaiseDesk
DROP TABLE IF EXISTS public.brand_dna CASCADE;
DROP TABLE IF EXISTS public.client_calls CASCADE;
DROP TABLE IF EXISTS public.client_communications CASCADE;
DROP TABLE IF EXISTS public.client_documents CASCADE;
DROP TABLE IF EXISTS public.client_kpis CASCADE;
DROP TABLE IF EXISTS public.client_photos CASCADE;
DROP TABLE IF EXISTS public.clients CASCADE;
DROP TABLE IF EXISTS public.company_settings CASCADE;
DROP TABLE IF EXISTS public.contacts CASCADE;
DROP TABLE IF EXISTS public.content_library CASCADE;
DROP TABLE IF EXISTS public.email_templates CASCADE;
DROP TABLE IF EXISTS public.employees CASCADE;
DROP TABLE IF EXISTS public.invoices CASCADE;
DROP TABLE IF EXISTS public.negative_reviews CASCADE;
DROP TABLE IF EXISTS public.onboarding CASCADE;
DROP TABLE IF EXISTS public.organizations CASCADE;
DROP TABLE IF EXISTS public.positive_review_redirects CASCADE;
DROP TABLE IF EXISTS public.products CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;
DROP TABLE IF EXISTS public.quick_notes CASCADE;
DROP TABLE IF EXISTS public.review_funnel_config CASCADE;
DROP TABLE IF EXISTS public.review_settings CASCADE;
DROP TABLE IF EXISTS public.scan_tracking CASCADE;
DROP TABLE IF EXISTS public.tasks CASCADE;

-- ============================================================================
-- VÉRIFICATION
-- ============================================================================
-- Vérifier que seules les tables Reputalys restent
SELECT 
    tablename,
    'Table conservée' as status
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

-- Afficher les tables restantes (devrait être vide ou ne contenir que les tables Reputalys)
SELECT 
    tablename,
    'Table à vérifier' as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename NOT IN (
    'conversations',
    'messages',
    'pricing',
    'crypto_addresses',
    'message_templates',
    'bot_messages',
    'bot_buttons'
)
ORDER BY tablename;

-- ============================================================================
-- ✅ NETTOYAGE TERMINÉ
-- ============================================================================
-- Les 7 tables Reputalys doivent être conservées :
-- - conversations
-- - messages
-- - pricing
-- - crypto_addresses
-- - message_templates
-- - bot_messages
-- - bot_buttons
-- ============================================================================

