import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DICT_PATH = ROOT / 'data' / 'translation.json'
NEW_LANGS = ['fr', 'pt', 'de', 'es', 'ja']

NAV_OVERRIDES = {
    'fr': {
        'home_nav': 'Accueil',
        'search_nav': 'Recherche',
        'tools_nav': 'Outils',
        'statistics_nav': 'Statistiques',
        'welcome_title': 'Bienvenue sur SPADE',
        'search_placeholder': 'Entrez une séquence de peptide...',
        'orientation_title': 'Meilleure expérience',
        'orientation_message': 'Pour une meilleure expérience, utilisez le mode paysage',
        'orientation_tip': 'Tournez votre appareil en mode paysage',
        'orientation_close': 'Fermer',
        'mobile_warning_title': 'Meilleur affichage sur ordinateur',
        'mobile_warning_text': 'Pour une meilleure expérience, visitez SPADE sur un ordinateur de bureau ou portable.',
        'search_category_all': 'Toutes catégories',
        'search_category_id': 'ID',
        'search_category_name': 'Nom',
        'search_category_sequence': 'Séquence',
        'SPADE Search': 'Recherche SPADE'
    },
    'pt': {
        'home_nav': 'Início',
        'search_nav': 'Pesquisa',
        'tools_nav': 'Ferramentas',
        'statistics_nav': 'Estatísticas',
        'welcome_title': 'Bem-vindo ao SPADE',
        'search_placeholder': 'Digite a sequência do peptídeo...',
        'orientation_title': 'Melhor experiência',
        'orientation_message': 'Para melhor experiência, use o modo paisagem',
        'orientation_tip': 'Gire seu dispositivo para o modo paisagem',
        'orientation_close': 'Fechar',
        'mobile_warning_title': 'Melhor visualização no desktop',
        'mobile_warning_text': 'Para a melhor experiência, visite o SPADE em um desktop ou notebook.',
        'search_category_all': 'Todas as categorias',
        'search_category_id': 'ID',
        'search_category_name': 'Nome',
        'search_category_sequence': 'Sequência',
        'SPADE Search': 'Busca SPADE'
    },
    'de': {
        'home_nav': 'Startseite',
        'search_nav': 'Suche',
        'tools_nav': 'Werkzeuge',
        'statistics_nav': 'Statistiken',
        'welcome_title': 'Willkommen bei SPADE',
        'search_placeholder': 'Peptidsequenz eingeben...',
        'orientation_title': 'Bessere Erfahrung',
        'orientation_message': 'Für die beste Erfahrung bitte Querformat verwenden',
        'orientation_tip': 'Drehen Sie Ihr Gerät ins Querformat',
        'orientation_close': 'Schließen',
        'mobile_warning_title': 'Beste Ansicht auf Desktop',
        'mobile_warning_text': 'Für die beste Erfahrung besuchen Sie SPADE auf einem Desktop- oder Laptop-Computer.',
        'search_category_all': 'Alle Kategorien',
        'search_category_id': 'ID',
        'search_category_name': 'Name',
        'search_category_sequence': 'Sequenz',
        'SPADE Search': 'SPADE Suche'
    },
    'es': {
        'home_nav': 'Inicio',
        'search_nav': 'Buscar',
        'tools_nav': 'Herramientas',
        'statistics_nav': 'Estadísticas',
        'welcome_title': 'Bienvenido a SPADE',
        'search_placeholder': 'Ingrese la secuencia del péptido...',
        'orientation_title': 'Mejor experiencia',
        'orientation_message': 'Para la mejor experiencia, use el modo paisaje',
        'orientation_tip': 'Gire su dispositivo al modo paisaje',
        'orientation_close': 'Cerrar',
        'mobile_warning_title': 'Mejor visto en escritorio',
        'mobile_warning_text': 'Para una experiencia óptima, visite SPADE en un ordenador de escritorio o portátil.',
        'search_category_all': 'Todas las categorías',
        'search_category_id': 'ID',
        'search_category_name': 'Nombre',
        'search_category_sequence': 'Secuencia',
        'SPADE Search': 'Búsqueda SPADE'
    },
    'ja': {
        'home_nav': 'ホーム',
        'search_nav': '検索',
        'tools_nav': 'ツール',
        'statistics_nav': '統計',
        'welcome_title': 'SPADE へようこそ',
        'search_placeholder': 'ペプチド配列を入力...',
        'orientation_title': 'より良い体験',
        'orientation_message': '最適な表示のため、横向きモードをご利用ください',
        'orientation_tip': '端末を横向きにしてください',
        'orientation_close': '閉じる',
        'mobile_warning_title': 'デスクトップでの閲覧を推奨',
        'mobile_warning_text': '最適な体験のため、デスクトップまたはノートPCでSPADEをご利用ください。',
        'search_category_all': 'すべてのカテゴリ',
        'search_category_id': 'ID',
        'search_category_name': '名称',
        'search_category_sequence': '配列',
        'SPADE Search': 'SPADE 検索'
    }
}

# 新增：从外部 JSON 覆盖翻译
def apply_overrides_from_json(data, lang, json_path):
    import json
    from pathlib import Path
    p = Path(json_path)
    if p.exists():
        try:
            overrides = json.loads(p.read_text(encoding='utf-8'))
            if isinstance(overrides, dict):
                data.setdefault(lang, {}).update(overrides)
        except Exception as e:
            print(f'Warn: failed to apply {json_path}:', e)

if __name__ == '__main__':
    if not DICT_PATH.exists():
        raise FileNotFoundError(f'Not found: {DICT_PATH}')

    data = json.loads(DICT_PATH.read_text(encoding='utf-8'))
    en = data.get('en', {})
    added_counts = {}

    for lang in NEW_LANGS:
        lang_dict = data.setdefault(lang, {})
        # Seed missing keys with English
        missing = 0
        for k, v in en.items():
            if k not in lang_dict:
                lang_dict[k] = v
                missing += 1
        added_counts[lang] = missing
        # Apply curated overrides for key UI labels
        overrides = NAV_OVERRIDES.get(lang, {})
        lang_dict.update(overrides)
        # 读取并应用外部 JSON 覆盖
        apply_overrides_from_json(data, lang, ROOT / 'program' / f'translations_{lang}.json')

    DICT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Done. Added placeholder keys:', added_counts)