#coding: utf-8

from xml.sax import ContentHandler
from xml.sax import parse
from common import TAG_TU, TAG_TUV, ATTR_TYPE, TYPE_SOURCE, ATTR_LANG, ATTR_FILE_SOURCE, ATTR_GENRE, TYPE_TRANSLATION, TAG_SEG, ATTR_GENDER, ATTR_EXPERIENCE, ATTR_MARK, ATTR_STAGE, ATTR_STRESS, ATTR_CONDITIONS, ATTR_YEAR, ATTR_AFFILIATION


class TranslationUnitVariation(object):
    def __init__(self, language, data_type, file_source, gender=None, experience=None, mark=None, stage=None,
                 genre=None, stress=None, conditions=None, year=None, affiliation=None):
        # обязательные
        self.language = language
        self.data_type = data_type
        self.file_source = file_source

        # необязательные
        self.gender = gender
        self.experience = experience
        self.mark = mark
        self.stage = stage
        self.genre = genre
        self.stress = stress
        self.conditions = conditions
        self.year = year
        self.affiliation = affiliation

        # http://www.gala-global.org/oscarStandards/tmx/tmx14b.html#tuv согласно доке всего один seg на tuv
        self.segment = None


class TranslationUnit(object):
    """Класс соответствующий одной единице перевода
    """
    def __init__(self):
        self.tuvs = []


class TMXFileHandler(ContentHandler):
    """Обработчик событий для разбора TMX файлов
    """
    def __init__(self, filtering_params):
        """ Конструктор

        :param filtering_params: словарь параметров фильтрации
            параметры фильтрации, должны содержать только параметры фильтрации
            gender: пол переводчика
            experience: возраст переводчика (курс)
            mark: оценка за перевод
            stage: степень законченности перевода
            genre: жанр текста
            stress: ситуация перевода
            conditions: условия перевода
            year: год
            data_type: тип данных
            affiliation: образовательное учреждение
        """
        ContentHandler.__init__(self)  # old-style class нельзя использовать с super()
        self.filtering_params = filtering_params

        # результаты
        self.tus = []
        self.current_tu = None
        self.current_tuv = None
        self.get_seg = False

    def startElement(self, name, attrs):
        if name == TAG_TU:
            self.current_tu = TranslationUnit()
        elif name == TAG_TUV:
            tag_type = attrs.get(ATTR_TYPE)
            genre = attrs.get(ATTR_GENRE)
            lang = attrs.get(ATTR_LANG)
            file_source = attrs.get(ATTR_FILE_SOURCE)

            if tag_type == TYPE_SOURCE and self.filter_source_type(genre):
                self.current_tuv = TranslationUnitVariation(lang, tag_type, file_source)
            elif tag_type == TYPE_TRANSLATION and self.filter_translation_type(attrs):
                gender = attrs.get(ATTR_GENDER)
                experience = attrs.get(ATTR_EXPERIENCE)
                mark = attrs.get(ATTR_MARK)
                stage = attrs.get(ATTR_STAGE)
                stress = attrs.get(ATTR_STRESS)
                conditions = attrs.get(ATTR_CONDITIONS)
                year = attrs.get(ATTR_YEAR)
                affiliation = attrs.get(ATTR_AFFILIATION)
                self.current_tuv = TranslationUnitVariation(lang, tag_type, file_source, gender, experience, mark,
                                                            stage, genre, stress, conditions, year, affiliation)
        elif name == TAG_SEG:
            #TODO здесь поиск
            self.get_seg = True

    def endElement(self, name):
        if name == TAG_TU and self.current_tu and self.current_tu.tuvs:
            # TODO берем только когда есть и перевод и оригинал
            self.tus.append(self.current_tu)
            self.current_tu = None
        if name == TAG_TUV and self.current_tuv:
            self.current_tu.tuvs.append(self.current_tuv)
            self.current_tuv = None

    def characters(self, content):
        # забираем содержимое сегмента
        if self.get_seg and self.current_tuv:
            self.current_tuv.segment = content
            self.get_seg = False

    def filter_source_type(self, genre):
        """Для источника, фильтр проверяет только по жанру
        """
        filter_genre = self.filtering_params.get(ATTR_GENRE)
        return not filter_genre or filter_genre == genre

    def filter_translation_type(self, tag_attrs):
        """Для переводов, фильтр проверяет по всем атрибутам
        """
        for filter_attr, filter_attr_value in self.filtering_params.items():
            if filter_attr != ATTR_TYPE and filter_attr_value and \
                    tag_attrs.get(filter_attr) != filter_attr_value:
                return False
        return True


def get_tmx_files():
    return ["data/rltc_small.tmx"]


def get_data_from_tmx(tmx_path, filtering_params):
    tmx_file = open(tmx_path, "r")
    tmx_handler = TMXFileHandler(filtering_params)

    try:
        parse(tmx_file, tmx_handler)
    except Exception, e:
        print e

    tmx_file.close()


def search(filtering_params):
    """Главный метод модуля. Обеспечивает фильтрацию содержимого tmx файла и поиск поотфильтрованным данным

    :param filtering_params: словарь параметров фильтрации
        параметры фильтрации, должны содержать только параметры фильтрации
        gender: пол переводчика
        experience: возраст переводчика (курс)
        mark: оценка за перевод
        stage: степень законченности перевода
        genre: жанр текста
        stress: ситуация перевода
        conditions: условия перевода
        year: год
        data_type: тип данных
        affiliation: образовательное учреждение
    """
    for tmx_file in get_tmx_files():
        get_data_from_tmx(tmx_file, filtering_params)


if __name__ == "__main__":
    search({"genre": "Informational", "type": "Source", "gender": "M", "year": "2008"})
