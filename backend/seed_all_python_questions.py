"""
Complete seed script for all Python topics.
Generates 20-30 questions per topic with English and Ukrainian translations.
Total: ~225 questions across 9 topics
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from learning.models import Topic, Question, AnswerOption

def create_question(topic, text_en, text_uk, difficulty, options_en, options_uk, 
                    correct_index=0, question_type='multiple_choice', 
                    explanation_en='', explanation_uk='', xp_reward=10):
    question = Question.objects.create(
        topic=topic,
        language='python',
        specialization='backend',
        difficulty=difficulty,
        question_type=question_type,
        xp_reward=xp_reward,
        is_active=True,
        text_en=text_en,
        text_uk=text_uk,
        text=text_en,
        explanation_en=explanation_en,
        explanation_uk=explanation_uk,
        explanation=explanation_en
    )
    question.save()
    
    for i, (opt_en, opt_uk) in enumerate(zip(options_en, options_uk)):
        option = AnswerOption.objects.create(
            question=question,
            text_en=opt_en,
            text_uk=opt_uk,
            text=opt_en,
            is_correct=(i == correct_index),
            order=i
        )
        option.save()
    
    return question


def get_or_create_topics():
    """Create all Python topics."""
    topics = {}
    
    topic_data = [
        {'key': 'basics', 'name': 'Python Basics', 'name_uk': 'Основи Python', 'icon': '🐍', 'order': 1},
        {'key': 'oop', 'name': 'Object Oriented Programming', 'name_uk': 'ООП в Python', 'icon': '📦', 'order': 2},
        {'key': 'decorators', 'name': 'Decorators & Closures', 'name_uk': 'Декоратори та Замикання', 'icon': '🎨', 'order': 3},
        {'key': 'generators', 'name': 'Generators & Iterators', 'name_uk': 'Генератори та Ітератори', 'icon': '⚡', 'order': 4},
        {'key': 'async', 'name': 'Async & Asyncio', 'name_uk': 'Асинхронність та Asyncio', 'icon': '🚀', 'order': 5},
        {'key': 'django_orm', 'name': 'Django ORM', 'name_uk': 'Django ORM', 'icon': '🗄️', 'order': 6},
        {'key': 'drf', 'name': 'Django REST Framework', 'name_uk': 'Django REST Framework', 'icon': '🔌', 'order': 7},
        {'key': 'architecture', 'name': 'Python Architecture', 'name_uk': 'Архітектура Python', 'icon': '🏗️', 'order': 8},
        {'key': 'advanced', 'name': 'Advanced Python', 'name_uk': 'Просунутий Python', 'icon': '🔥', 'order': 9},
    ]
    
    for data in topic_data:
        topic, created = Topic.objects.get_or_create(
            language='python',
            name_en=data['name'],
            defaults={
                'name': data['name'],
                'name_uk': data['name_uk'],
                'icon': data['icon'],
                'order': data['order'],
                'is_active': True
            }
        )
        topics[data['key']] = topic
    
    return topics


def seed_basics_questions(topic):
    """25 questions for Python Basics."""
    questions = [
        {
            'text_en': "What is the output of `print(type([]))`?",
            'text_uk': "Що виведе `print(type([]))`?",
            'difficulty': 'easy',
            'options_en': ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'array'>"],
            'options_uk': ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'array'>"],
            'correct': 0,
            'explanation_en': "[] creates an empty list in Python",
            'explanation_uk': "[] створює порожній список в Python"
        },
        {
            'text_en': "Are strings in Python immutable?",
            'text_uk': "Чи є рядки (str) в Python незмінними (immutable)?",
            'difficulty': 'easy',
            'options_en': ["True", "False"],
            'options_uk': ["True", "False"],
            'correct': 0,
            'question_type': 'true_false',
            'explanation_en': "Strings in Python are immutable",
            'explanation_uk': "Рядки в Python є незмінними"
        },
        {
            'text_en': "What is the output of `print(bool(0), bool(''), bool([]))`?",
            'text_uk': "Що виведе `print(bool(0), bool(''), bool([]))`?",
            'difficulty': 'easy',
            'options_en': ["False False False", "True True True", "False True False", "None None None"],
            'options_uk': ["False False False", "True True True", "False True False", "None None None"],
            'correct': 0,
            'explanation_en': "0, empty string, and empty list are all falsy values",
            'explanation_uk': "0, порожній рядок і порожній список є falsy значеннями"
        },
        {
            'text_en': "What is the difference between `is` and `==`?",
            'text_uk': "Яка різниця між `is` та `==`?",
            'difficulty': 'easy',
            'options_en': ["`is` checks identity, `==` checks equality", "`is` checks equality, `==` checks identity", "They are the same", "`is` is for strings only"],
            'options_uk': ["`is` перевіряє тотожність, `==` перевіряє рівність", "`is` перевіряє рівність, `==` перевіряє тотожність", "Вони однакові", "`is` тільки для рядків"],
            'correct': 0,
            'explanation_en': "`is` checks if objects are same in memory, `==` checks value equality",
            'explanation_uk': "`is` перевіряє чи об'єкти однакові в пам'яті, `==` перевіряє рівність значень"
        },
        {
            'text_en': "What does `*args` mean?",
            'text_uk': "Що означає `*args`?",
            'difficulty': 'medium',
            'options_en': ["Tuple of positional arguments", "List of arguments", "Dictionary of arguments", "Single argument"],
            'options_uk': ["Tuple позиційних аргументів", "Список аргументів", "Словник аргументів", "Один аргумент"],
            'correct': 0,
            'explanation_en': "*args collects positional arguments as a tuple",
            'explanation_uk': "*args збирає позиційні аргументи як tuple"
        },
        {
            'text_en': "What is the output?\n```python\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)\n```",
            'text_uk': "Що виведе цей код?\n```python\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)\n```",
            'difficulty': 'medium',
            'options_en': ["[1, 2, 3, 4]", "[1, 2, 3]", "Error", "None"],
            'options_uk': ["[1, 2, 3, 4]", "[1, 2, 3]", "Помилка", "None"],
            'correct': 0,
            'explanation_en': "b = a creates a reference to the same list",
            'explanation_uk': "b = a створює посилання на той самий список"
        },
        {
            'text_en': "What is list comprehension?",
            'text_uk': "Що таке list comprehension?",
            'difficulty': 'medium',
            'options_en': ["A concise way to create lists", "A type of loop", "A function", "A list method"],
            'options_uk': ["Стислий спосіб створення списків", "Тип циклу", "Функція", "Метод списку"],
            'correct': 0,
            'explanation_en': "[x for x in range(10)] is list comprehension",
            'explanation_uk': "[x for x in range(10)] це list comprehension"
        },
        {
            'text_en': "What is the output?\n```python\ndef func(x=[]):\n    x.append(1)\n    return x\nprint(func())\nprint(func())\n```",
            'text_uk': "Що виведе цей код?\n```python\ndef func(x=[]):\n    x.append(1)\n    return x\nprint(func())\nprint(func())\n```",
            'difficulty': 'hard',
            'options_en': ["[1], [1, 1]", "[1], [1]", "Error", "[1, 1], [1, 1]"],
            'options_uk': ["[1], [1, 1]", "[1], [1]", "Помилка", "[1, 1], [1, 1]"],
            'correct': 0,
            'explanation_en': "Default mutable arguments are created once when function is defined",
            'explanation_uk': "Мутабельні аргументи за замовчуванням створюються один раз"
        },
        {
            'text_en': "What is `__slots__`?",
            'text_uk': "Що таке `__slots__`?",
            'difficulty': 'hard',
            'options_en': ["Restricts attributes and saves memory", "A decorator", "A method", "Private variables"],
            'options_uk': ["Обмежує атрибути та економить пам'ять", "Декоратор", "Метод", "Приватні змінні"],
            'correct': 0,
            'explanation_en': "__slots__ prevents __dict__ creation and saves memory",
            'explanation_uk': "__slots__ запобігає створенню __dict__ та економить пам'ять"
        },
        {
            'text_en': "What is GIL?",
            'text_uk': "Що таке GIL?",
            'difficulty': 'hard',
            'options_en': ["Global Interpreter Lock - 1 thread at a time", "Global Integration Library", "Package manager", "Testing framework"],
            'options_uk': ["Global Interpreter Lock - 1 потік одночасно", "Global Integration Library", "Менеджер пакетів", "Фреймворк для тестування"],
            'correct': 0,
            'explanation_en': "GIL allows only one thread to execute Python bytecode at a time",
            'explanation_uk': "GIL дозволяє тільки одному потоку виконувати Python байткод"
        },
        {
            'text_en': "What is the difference between deep and shallow copy?",
            'text_uk': "Яка різниця між глибоким та поверхневим копіюванням?",
            'difficulty': 'medium',
            'options_en': ["Shallow references nested, deep copies all", "They are the same", "Deep is faster", "Shallow only for lists"],
            'options_uk': ["Shallow посилається на вкладені, deep копіює все", "Вони однакові", "Deep швидший", "Shallow тільки для списків"],
            'correct': 0,
        },
        {
            'text_en': "What does `__name__ == '__main__'` do?",
            'text_uk': "Що робить `__name__ == '__main__'`?",
            'difficulty': 'easy',
            'options_en': ["Checks if script run directly vs imported", "Defines main function", "Imports module", "Creates namespace"],
            'options_uk': ["Перевіряє чи скрипт запущено безпосередньо", "Визначає головну функцію", "Імпортує модуль", "Створює простір імен"],
            'correct': 0,
        },
        {
            'text_en': "What is a lambda function?",
            'text_uk': "Що таке lambda функція?",
            'difficulty': 'easy',
            'options_en': ["Anonymous single-expression function", "A class", "A decorator", "A module"],
            'options_uk': ["Анонімна функція з одним виразом", "Клас", "Декоратор", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is output of `print(2 ** 3 ** 2)`?",
            'text_uk': "Що виведе `print(2 ** 3 ** 2)`?",
            'difficulty': 'medium',
            'options_en': ["512", "64", "72", "36"],
            'options_uk': ["512", "64", "72", "36"],
            'correct': 0,
            'explanation_en': "Right-associative: 2 ** (3 ** 2) = 2 ** 9 = 512",
            'explanation_uk': "Правоасоціативне: 2 ** (3 ** 2) = 2 ** 9 = 512"
        },
        {
            'text_en': "What is `__init__` vs `__new__`?",
            'text_uk': "Що таке `__init__` проти `__new__`?",
            'difficulty': 'hard',
            'options_en': ["__new__ creates, __init__ initializes", "Same thing", "__init__ creates", "__new__ for classes only"],
            'options_uk': ["__new__ створює, __init__ ініціалізує", "Одне й те саме", "__init__ створює", "__new__ тільки для класів"],
            'correct': 0,
        },
        {
            'text_en': "What is the difference between `range()` and list?",
            'text_uk': "Яка різниця між `range()` та списком?",
            'difficulty': 'easy',
            'options_en': ["range() is lazy, list stores all values", "Same thing", "range() faster", "List only numbers"],
            'options_uk': ["range() лінивий, список зберігає все", "Одне й те саме", "range() швидший", "Список тільки числа"],
            'correct': 0,
        },
        {
            'text_en': "What does `zip()` do?",
            'text_uk': "Що робить `zip()`?",
            'difficulty': 'easy',
            'options_en': ["Combines iterables element-wise", "Compresses data", "Sorts list", "Filters elements"],
            'options_uk': ["Поєднує ітерабельні поелементно", "Стискає дані", "Сортує список", "Фільтрує елементи"],
            'correct': 0,
        },
        {
            'text_en': "What is a set?",
            'text_uk': "Що таке множина (set)?",
            'difficulty': 'easy',
            'options_en': ["Unordered collection of unique elements", "Ordered list", "Dictionary type", "Special tuple"],
            'options_uk': ["Невпорядкована колекція унікальних елементів", "Впорядкований список", "Тип словника", "Спеціальний кортеж"],
            'correct': 0,
        },
        {
            'text_en': "What is output of `print('Python'[-3:])`?",
            'text_uk': "Що виведе `print('Python'[-3:])`?",
            'difficulty': 'medium',
            'options_en': ["hon", "Pyt", "tho", "n"],
            'options_uk': ["hon", "Pyt", "tho", "n"],
            'correct': 0,
        },
        {
            'text_en': "Difference between `append()` and `extend()`?",
            'text_uk': "Різниця між `append()` та `extend()`?",
            'difficulty': 'medium',
            'options_en': ["append adds one element, extend adds from iterable", "Same", "append faster", "extend only tuples"],
            'options_uk': ["append додає один елемент, extend додає з ітерабельного", "Однакові", "append швидший", "extend тільки кортежі"],
            'correct': 0,
        },
        {
            'text_en': "What is `*` (unpacking) operator?",
            'text_uk': "Що таке оператор `*` (розпакування)?",
            'difficulty': 'medium',
            'options_en': ["Unpacks iterable into elements", "Multiplies", "Creates pointer", "Defines decorator"],
            'options_uk': ["Розпаковує ітерабельний на елементи", "Множить", "Створює вказівник", "Визначає декоратор"],
            'correct': 0,
        },
        {
            'text_en': "What is `pass` statement?",
            'text_uk': "Що таке оператор `pass`?",
            'difficulty': 'easy',
            'options_en': ["Null operation - placeholder", "Skips iteration", "Exits loop", "Continues"],
            'options_uk': ["Порожня операція - заповнювач", "Пропускає ітерацію", "Виходить з циклу", "Продовжує"],
            'correct': 0,
        },
        {
            'text_en': "Difference between `sort()` and `sorted()`?",
            'text_uk': "Різниця між `sort()` та `sorted()`?",
            'difficulty': 'medium',
            'options_en': ["sort() in-place, sorted() returns new list", "Same", "sort() faster", "sorted() only numbers"],
            'options_uk': ["sort() на місці, sorted() повертає новий", "Однакові", "sort() швидший", "sorted() тільки числа"],
            'correct': 0,
        },
        {
            'text_en': "What is dictionary comprehension?",
            'text_uk': "Що таке dictionary comprehension?",
            'difficulty': 'medium',
            'options_en': ["Concise way to create dicts: {k: v for ...}", "Loop type", "Dict method", "Iteration way"],
            'options_uk': ["Стислий спосіб створення словників: {k: v for ...}", "Тип циклу", "Метод словника", "Спосіб ітерації"],
            'correct': 0,
        },
        {
            'text_en': "What is output of `print(len({1, 2, 2, 3}))`?",
            'text_uk': "Що виведе `print(len({1, 2, 2, 3}))`?",
            'difficulty': 'easy',
            'options_en': ["3", "4", "2", "Error"],
            'options_uk': ["3", "4", "2", "Помилка"],
            'correct': 0,
            'explanation_en': "Sets remove duplicates, so {1, 2, 2, 3} = {1, 2, 3}",
            'explanation_uk': "Множини видаляють дублікати, тому {1, 2, 2, 3} = {1, 2, 3}"
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            question_type=q.get('question_type', 'multiple_choice'),
            explanation_en=q.get('explanation_en', ''),
            explanation_uk=q.get('explanation_uk', ''),
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_oop_questions(topic):
    """25 questions for OOP."""
    questions = [
        {
            'text_en': "What is `self` in Python class?",
            'text_uk': "Що таке `self` в класі Python?",
            'difficulty': 'easy',
            'options_en': ["Reference to instance", "A keyword", "A module", "A decorator"],
            'options_uk': ["Посилання на екземпляр", "Ключове слово", "Модуль", "Декоратор"],
            'correct': 0,
        },
        {
            'text_en': "Difference between `@classmethod` and `@staticmethod`?",
            'text_uk': "Різниця між `@classmethod` та `@staticmethod`?",
            'difficulty': 'easy',
            'options_en': ["classmethod gets cls, staticmethod gets nothing", "Same", "staticmethod gets cls", "classmethod only for private"],
            'options_uk': ["classmethod отримує cls, staticmethod нічого", "Однакові", "staticmethod отримує cls", "classmethod тільки для приватних"],
            'correct': 0,
        },
        {
            'text_en': "What is `@property`?",
            'text_uk': "Що таке `@property`?",
            'difficulty': 'medium',
            'options_en': ["Decorator for getter methods", "A class", "A module", "A variable"],
            'options_uk': ["Декоратор для getter методів", "Клас", "Модуль", "Змінна"],
            'correct': 0,
        },
        {
            'text_en': "What is multiple inheritance?",
            'text_uk': "Що таке множинне успадкування?",
            'difficulty': 'medium',
            'options_en': ["Class inherits from multiple parents", "Multiple classes one parent", "Same thing", "Interface"],
            'options_uk': ["Клас успадковує від кількох батьків", "Кілька класів один батько", "Одне й те саме", "Інтерфейс"],
            'correct': 0,
        },
        {
            'text_en': "What is MRO?",
            'text_uk': "Що таке MRO?",
            'difficulty': 'hard',
            'options_en': ["Method Resolution Order - order of inheritance lookup", "Memory Runtime Object", "Module Reference", "Method Reference"],
            'options_uk': ["Method Resolution Order - порядок пошуку успадкування", "Memory Runtime Object", "Module Reference", "Method Reference"],
            'correct': 0,
        },
        {
            'text_en': "What are dunder methods?",
            'text_uk': "Що таке dunder методи?",
            'difficulty': 'hard',
            'options_en': ["Magic methods like __init__, __str__", "Private methods", "Static methods", "Class methods"],
            'options_uk': ["Магічні методи як __init__, __str__", "Приватні методи", "Статичні методи", "Методи класу"],
            'correct': 0,
        },
        {
            'text_en': "How to create abstract class?",
            'text_uk': "Як створити абстрактний клас?",
            'difficulty': 'hard',
            'options_en': ["from abc import ABC, abstractmethod", "abstract class MyClass", "class @abstract", "Using @abstractmethod only"],
            'options_uk': ["from abc import ABC, abstractmethod", "abstract class MyClass", "class @abstract", "Тільки @abstractmethod"],
            'correct': 0,
        },
        {
            'text_en': "What is encapsulation?",
            'text_uk': "Що таке інкапсуляція?",
            'difficulty': 'easy',
            'options_en': ["Bundling data and methods", "Inheritance", "Polymorphism", "Abstraction"],
            'options_uk': ["Об'єднання даних і методів", "Успадкування", "Поліморфізм", "Абстракція"],
            'correct': 0,
        },
        {
            'text_en': "What is polymorphism?",
            'text_uk': "Що таке поліморфізм?",
            'difficulty': 'easy',
            'options_en': ["Same interface, different implementations", "Multiple inheritance", "Encapsulation", "Abstraction"],
            'options_uk': ["Один інтерфейс, різні реалізації", "Множинне успадкування", "Інкапсуляція", "Абстракція"],
            'correct': 0,
        },
        {
            'text_en': "What is `__str__` vs `__repr__`?",
            'text_uk': "Що таке `__str__` проти `__repr__`?",
            'difficulty': 'medium',
            'options_en': ["__str__ for users, __repr__ for developers", "Same", "__repr__ for users", "No difference"],
            'options_uk': ["__str__ для користувачів, __repr__ для розробників", "Однакові", "__repr__ для користувачів", "Немає різниці"],
            'correct': 0,
        },
        {
            'text_en': "What is composition?",
            'text_uk': "Що таке композиція?",
            'difficulty': 'medium',
            'options_en': ["Building complex objects from simpler ones", "Inheritance", "Polymorphism", "Encapsulation"],
            'options_uk': ["Створення складних об'єктів з простіших", "Успадкування", "Поліморфізм", "Інкапсуляція"],
            'correct': 0,
        },
        {
            'text_en': "What is `super()`?",
            'text_uk': "Що таке `super()`?",
            'difficulty': 'easy',
            'options_en': ["Call parent class methods", "Create instance", "Delete object", "Check type"],
            'options_uk': ["Викликати методи батьківського класу", "Створити екземпляр", "Видалити об'єкт", "Перевірити тип"],
            'correct': 0,
        },
        {
            'text_en': "What is name mangling?",
            'text_uk': "Що таке name mangling?",
            'difficulty': 'hard',
            'options_en': ["_Class__var for private attributes", "Public attributes", "Static methods", "Decorators"],
            'options_uk': ["_Class__var для приватних атрибутів", "Публічні атрибути", "Статичні методи", "Декоратори"],
            'correct': 0,
        },
        {
            'text_en': "What is `__call__` method?",
            'text_uk': "Що таке метод `__call__`?",
            'difficulty': 'hard',
            'options_en': ["Makes instance callable like function", "Constructor", "Destructor", "Iterator"],
            'options_uk': ["Робить екземпляр викликаним як функція", "Конструктор", "Деструктор", "Ітератор"],
            'correct': 0,
        },
        {
            'text_en': "What is `__enter__` and `__exit__`?",
            'text_uk': "Що таке `__enter__` та `__exit__`?",
            'difficulty': 'hard',
            'options_en': ["Context manager protocol", "Constructor", "Destructor", "Iterator"],
            'options_uk': ["Протокол контекстного менеджера", "Конструктор", "Деструктор", "Ітератор"],
            'correct': 0,
        },
        {
            'text_en': "What is `isinstance()`?",
            'text_uk': "Що таке `isinstance()`?",
            'difficulty': 'easy',
            'options_en': ["Check if object is instance of class", "Create instance", "Delete object", "Get type"],
            'options_uk': ["Перевірити чи об'єкт екземпляр класу", "Створити екземпляр", "Видалити об'єкт", "Отримати тип"],
            'correct': 0,
        },
        {
            'text_en': "What is `__dict__`?",
            'text_uk': "Що таке `__dict__`?",
            'difficulty': 'medium',
            'options_en': ["Dictionary of object attributes", "Method", "Class", "Module"],
            'options_uk': ["Словник атрибутів об'єкта", "Метод", "Клас", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is descriptor?",
            'text_uk': "Що таке дескриптор?",
            'difficulty': 'hard',
            'options_en': ["Object with __get__, __set__, __delete__", "Decorator", "Property", "Method"],
            'options_uk': ["Об'єкт з __get__, __set__, __delete__", "Декоратор", "Властивість", "Метод"],
            'correct': 0,
        },
        {
            'text_en': "What is `__del__`?",
            'text_uk': "Що таке `__del__`?",
            'difficulty': 'medium',
            'options_en': ["Destructor called on object deletion", "Constructor", "Getter", "Setter"],
            'options_uk': ["Деструктор викликається при видаленні", "Конструктор", "Getter", "Setter"],
            'correct': 0,
        },
        {
            'text_en': "What is metaclass?",
            'text_uk': "Що таке метаклас?",
            'difficulty': 'hard',
            'options_en': ["Class that creates classes", "Instance", "Object", "Module"],
            'options_uk': ["Клас, який створює класи", "Екземпляр", "Об'єкт", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is `__getattr__`?",
            'text_uk': "Що таке `__getattr__`?",
            'difficulty': 'hard',
            'options_en': ["Called when attribute not found", "Constructor", "Getter", "Setter"],
            'options_uk': ["Викликається коли атрибут не знайдено", "Конструктор", "Getter", "Setter"],
            'correct': 0,
        },
        {
            'text_en': "What is `__len__`?",
            'text_uk': "Що таке `__len__`?",
            'difficulty': 'easy',
            'options_en': ["Returns object length", "Constructor", "Destructor", "Iterator"],
            'options_uk': ["Повертає довжину об'єкта", "Конструктор", "Деструктор", "Ітератор"],
            'correct': 0,
        },
        {
            'text_en': "What is `__iter__`?",
            'text_uk': "Що таке `__iter__`?",
            'difficulty': 'medium',
            'options_en': ["Returns iterator", "Constructor", "Destructor", "Getter"],
            'options_uk': ["Повертає ітератор", "Конструктор", "Деструктор", "Getter"],
            'correct': 0,
        },
        {
            'text_en': "What is `__next__`?",
            'text_uk': "Що таке `__next__`?",
            'difficulty': 'medium',
            'options_en': ["Returns next item from iterator", "Constructor", "Destructor", "Getter"],
            'options_uk': ["Повертає наступний елемент з ітератора", "Конструктор", "Деструктор", "Getter"],
            'correct': 0,
        },
        {
            'text_en': "What is `__eq__`?",
            'text_uk': "Що таке `__eq__`?",
            'difficulty': 'easy',
            'options_en': ["Equality comparison", "Constructor", "Destructor", "Getter"],
            'options_uk': ["Порівняння на рівність", "Конструктор", "Деструктор", "Getter"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_decorators_questions(topic):
    """20 questions for Decorators & Closures."""
    questions = [
        {
            'text_en': "What is a closure?",
            'text_uk': "Що таке замикання?",
            'difficulty': 'easy',
            'options_en': ["Function with captured variables", "Class", "Module", "Decorator"],
            'options_uk': ["Функція з захопленими змінними", "Клас", "Модуль", "Декоратор"],
            'correct': 0,
        },
        {
            'text_en': "What does @decorator do?",
            'text_uk': "Що робить @decorator?",
            'difficulty': 'easy',
            'options_en': ["Modifies function behavior", "Deletes function", "Creates class", "Imports module"],
            'options_uk': ["Змінює поведінку функції", "Видаляє функцію", "Створює клас", "Імпортує модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is @functools.wraps?",
            'text_uk': "Що таке @functools.wraps?",
            'difficulty': 'medium',
            'options_en': ["Preserves function metadata", "Decorator", "Module", "Class"],
            'options_uk': ["Зберігає метадані функції", "Декоратор", "Модуль", "Клас"],
            'correct': 0,
        },
        {
            'text_en': "How to create decorator with arguments?",
            'text_uk': "Як створити декоратор з аргументами?",
            'difficulty': 'hard',
            'options_en': ["Decorator factory returns decorator", "Direct arguments", "Not possible", "Using class"],
            'options_uk': ["Фабрика декораторів повертає декоратор", "Безпосередні аргументи", "Неможливо", "Використовуючи клас"],
            'correct': 0,
        },
        {
            'text_en': "What is output?\n```python\ndef deco(func):\n    def wrapper():\n        print('before')\n        func()\n        print('after')\n    return wrapper\n\n@deco\ndef hello():\n    print('hello')\n\nhello()\n```",
            'text_uk': "Що виведе цей код?",
            'difficulty': 'medium',
            'options_en': ["before, hello, after", "hello", "before, after", "Error"],
            'options_uk': ["before, hello, after", "hello", "before, after", "Помилка"],
            'correct': 0,
        },
        {
            'text_en': "What is @staticmethod?",
            'text_uk': "Що таке @staticmethod?",
            'difficulty': 'easy',
            'options_en': ["Method without self or cls", "Class method", "Instance method", "Property"],
            'options_uk': ["Метод без self або cls", "Метод класу", "Метод екземпляра", "Властивість"],
            'correct': 0,
        },
        {
            'text_en': "What is @classmethod?",
            'text_uk': "Що таке @classmethod?",
            'difficulty': 'easy',
            'options_en': ["Method receives cls as first arg", "Static method", "Instance method", "Property"],
            'options_uk': ["Метод отримує cls як перший аргумент", "Статичний метод", "Метод екземпляра", "Властивість"],
            'correct': 0,
        },
        {
            'text_en': "What is @property used for?",
            'text_uk': "Для чого використовується @property?",
            'difficulty': 'medium',
            'options_en': ["Create getter/setter", "Static method", "Class method", "Module"],
            'options_uk': ["Створити getter/setter", "Статичний метод", "Метод класу", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "Can decorators be chained?",
            'text_uk': "Чи можна ланцюжувати декоратори?",
            'difficulty': 'medium',
            'options_en': ["Yes, @decorator1 @decorator2 def func()", "No", "Only 2", "Only for classes"],
            'options_uk': ["Так, @decorator1 @decorator2 def func()", "Ні", "Тільки 2", "Тільки для класів"],
            'correct': 0,
        },
        {
            'text_en': "What is nonlocal keyword?",
            'text_uk': "Що таке ключове слово nonlocal?",
            'difficulty': 'hard',
            'options_en': ["Access outer scope variable", "Global variable", "Local variable", "Class variable"],
            'options_uk': ["Доступ до змінної зовнішньої області", "Глобальна змінна", "Локальна змінна", "Змінна класу"],
            'correct': 0,
        },
        {
            'text_en': "What is @lru_cache?",
            'text_uk': "Що таке @lru_cache?",
            'difficulty': 'medium',
            'options_en': ["Memoization decorator", "Logging", "Error handling", "Timing"],
            'options_uk': ["Декоратор мемоізації", "Логування", "Обробка помилок", "Вимірювання часу"],
            'correct': 0,
        },
        {
            'text_en': "What is @contextmanager?",
            'text_uk': "Що таке @contextmanager?",
            'difficulty': 'hard',
            'options_en': ["Creates context manager from generator", "Decorator", "Class", "Module"],
            'options_uk': ["Створює контекстний менеджер з генератора", "Декоратор", "Клас", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is @singledispatch?",
            'text_uk': "Що таке @singledispatch?",
            'difficulty': 'hard',
            'options_en': ["Function overloading by type", "Singleton", "Cache", "Timing"],
            'options_uk': ["Перевантаження функції за типом", "Синглтон", "Кеш", "Вимірювання часу"],
            'correct': 0,
        },
        {
            'text_en': "What is @dataclass?",
            'text_uk': "Що таке @dataclass?",
            'difficulty': 'medium',
            'options_en': ["Auto-generates special methods", "Decorator", "Module", "Function"],
            'options_uk': ["Автоматично генерує спеціальні методи", "Декоратор", "Модуль", "Функція"],
            'correct': 0,
        },
        {
            'text_en': "What is @abstractmethod?",
            'text_uk': "Що таке @abstractmethod?",
            'difficulty': 'medium',
            'options_en': ["Marks method as abstract", "Static method", "Class method", "Property"],
            'options_uk': ["Позначає метод як абстрактний", "Статичний метод", "Метод класу", "Властивість"],
            'correct': 0,
        },
        {
            'text_en': "What is @cached_property?",
            'text_uk': "Що таке @cached_property?",
            'difficulty': 'hard',
            'options_en': ["Property cached after first access", "Regular property", "Static method", "Class method"],
            'options_uk': ["Властивість кешується після першого доступу", "Звичайна властивість", "Статичний метод", "Метод класу"],
            'correct': 0,
        },
        {
            'text_en': "What is @wraps equivalent to?",
            'text_uk': "Чому еквівалентний @wraps?",
            'difficulty': 'hard',
            'options_en': ["update_wrapper function", "Decorator", "Module", "Class"],
            'options_uk': ["Функція update_wrapper", "Декоратор", "Модуль", "Клас"],
            'correct': 0,
        },
        {
            'text_en': "What is @deprecated?",
            'text_uk': "Що таке @deprecated?",
            'difficulty': 'easy',
            'options_en': ["Marks function as obsolete", "Static method", "Class method", "Property"],
            'options_uk': ["Позначає функцію як застарілу", "Статичний метод", "Метод класу", "Властивість"],
            'correct': 0,
        },
        {
            'text_en': "Can class be decorator?",
            'text_uk': "Чи може клас бути декоратором?",
            'difficulty': 'hard',
            'options_en': ["Yes, with __call__ method", "No", "Only with __init__", "Only abstract"],
            'options_uk': ["Так, з методом __call__", "Ні", "Тільки з __init__", "Тільки абстрактний"],
            'correct': 0,
        },
        {
            'text_en': "What is @retry decorator pattern?",
            'text_uk': "Що таке патерн декоратора @retry?",
            'difficulty': 'hard',
            'options_en': ["Retries function on failure", "Logging", "Caching", "Timing"],
            'options_uk': ["Повторює функцію при помилці", "Логування", "Кешування", "Вимірювання часу"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_generators_questions(topic):
    """20 questions for Generators & Iterators."""
    questions = [
        {
            'text_en': "What is difference between range() and list?",
            'text_uk': "Яка різниця між range() та списком?",
            'difficulty': 'easy',
            'options_en': ["range() is lazy generator-like", "Same", "range() faster", "List only numbers"],
            'options_uk': ["range() лінивий як генератор", "Однакові", "range() швидший", "Список тільки числа"],
            'correct': 0,
        },
        {
            'text_en': "What is generator?",
            'text_uk': "Що таке генератор?",
            'difficulty': 'easy',
            'options_en': ["Function that yields values", "Class", "Module", "Decorator"],
            'options_uk': ["Функція, яка повертає значення через yield", "Клас", "Модуль", "Декоратор"],
            'correct': 0,
        },
        {
            'text_en': "What does yield do?",
            'text_uk': "Що робить yield?",
            'difficulty': 'easy',
            'options_en': ["Returns value and pauses function", "Returns and exits", "Prints value", "Stores value"],
            'options_uk': ["Повертає значення і паузує функцію", "Повертає і виходить", "Друкує значення", "Зберігає значення"],
            'correct': 0,
        },
        {
            'text_en': "What is iterator?",
            'text_uk': "Що таке ітератор?",
            'difficulty': 'easy',
            'options_en': ["Object with __iter__ and __next__", "List", "Tuple", "Dictionary"],
            'options_uk': ["Об'єкт з __iter__ та __next__", "Список", "Кортеж", "Словник"],
            'correct': 0,
        },
        {
            'text_en': "What is output?\n```python\ndef gen():\n    yield 1\n    yield 2\n\ng = gen()\nprint(next(g))\nprint(next(g))\n```",
            'text_uk': "Що виведе цей код?",
            'difficulty': 'medium',
            'options_en': ["1, 2", "1, 1", "2, 2", "Error"],
            'options_uk': ["1, 2", "1, 1", "2, 2", "Помилка"],
            'correct': 0,
        },
        {
            'text_en': "What is generator expression?",
            'text_uk': "Що таке вираз-генератор?",
            'difficulty': 'medium',
            'options_en': ["(x for x in iterable)", "[x for x in iterable]", "{x for x in iterable}", "lambda x: x"],
            'options_uk': ["(x for x in iterable)", "[x for x in iterable]", "{x for x in iterable}", "lambda x: x"],
            'correct': 0,
        },
        {
            'text_en': "What is StopIteration?",
            'text_uk': "Що таке StopIteration?",
            'difficulty': 'medium',
            'options_en': ["Exception when iterator exhausted", "Error", "Warning", "Module"],
            'options_uk': ["Виключення коли ітератор вичерпано", "Помилка", "Попередження", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is yield from?",
            'text_uk': "Що таке yield from?",
            'difficulty': 'hard',
            'options_en': ["Delegates to subgenerator", "Returns generator", "Creates iterator", "Exits"],
            'options_uk': ["Делегує підгенератору", "Повертає генератор", "Створює ітератор", "Виходить"],
            'correct': 0,
        },
        {
            'text_en': "Can generator be reused?",
            'text_uk': "Чи можна повторно використати генератор?",
            'difficulty': 'medium',
            'options_en': ["No, exhausted after one use", "Yes", "Sometimes", "Only with reset"],
            'options_uk': ["Ні, вичерпується після одного використання", "Так", "Іноді", "Тільки з reset"],
            'correct': 0,
        },
        {
            'text_en': "What is itertools?",
            'text_uk': "Що таке itertools?",
            'difficulty': 'medium',
            'options_en': ["Module with iterator utilities", "Class", "Function", "Decorator"],
            'options_uk': ["Модуль з утилітами ітераторів", "Клас", "Функція", "Декоратор"],
            'correct': 0,
        },
        {
            'text_en': "What is itertools.chain?",
            'text_uk': "Що таке itertools.chain?",
            'difficulty': 'medium',
            'options_en': ["Chains multiple iterables", "Creates list", "Sorts", "Filters"],
            'options_uk': ["Ланцюжує кілька ітерабельних", "Створює список", "Сортує", "Фільтрує"],
            'correct': 0,
        },
        {
            'text_en': "What is itertools.groupby?",
            'text_uk': "Що таке itertools.groupby?",
            'difficulty': 'hard',
            'options_en': ["Groups consecutive elements", "SQL GROUP BY", "Sorts", "Filters"],
            'options_uk': ["Групує послідовні елементи", "SQL GROUP BY", "Сортує", "Фільтрує"],
            'correct': 0,
        },
        {
            'text_en': "What is itertools.islice?",
            'text_uk': "Що таке itertools.islice?",
            'difficulty': 'hard',
            'options_en': ["Slice of iterator", "List slice", "String slice", "Array slice"],
            'options_uk': ["Зріз ітератора", "Зріз списку", "Зріз рядка", "Зріз масиву"],
            'correct': 0,
        },
        {
            'text_en': "What is coroutine?",
            'text_uk': "Що таке корутина?",
            'difficulty': 'hard',
            'options_en': ["Generator that can receive data", "Function", "Class", "Thread"],
            'options_uk': ["Генератор, який може отримувати дані", "Функція", "Клас", "Потік"],
            'correct': 0,
        },
        {
            'text_en': "What is send() method?",
            'text_uk': "Що таке метод send()?",
            'difficulty': 'hard',
            'options_en': ["Sends value into generator", "Receives value", "Exits", "Resets"],
            'options_uk': ["Надсилає значення в генератор", "Отримує значення", "Виходить", "Скидає"],
            'correct': 0,
        },
        {
            'text_en': "What is throw() method?",
            'text_uk': "Що таке метод throw()?",
            'difficulty': 'hard',
            'options_en': ["Raises exception in generator", "Sends value", "Exits", "Resets"],
            'options_uk': ["Піднімає виключення в генераторі", "Надсилає значення", "Виходить", "Скидає"],
            'correct': 0,
        },
        {
            'text_en': "What is close() method?",
            'text_uk': "Що таке метод close()?",
            'difficulty': 'medium',
            'options_en': ["Closes generator", "Sends value", "Exits", "Resets"],
            'options_uk': ["Закриває генератор", "Надсилає значення", "Виходить", "Скидає"],
            'correct': 0,
        },
        {
            'text_en': "What is itertools.count?",
            'text_uk': "Що таке itertools.count?",
            'difficulty': 'easy',
            'options_en': ["Infinite counter iterator", "List counter", "String counter", "Array counter"],
            'options_uk': ["Нескінченний лічильник", "Лічильник списку", "Лічильник рядка", "Лічильник масиву"],
            'correct': 0,
        },
        {
            'text_en': "What is itertools.cycle?",
            'text_uk': "Що таке itertools.cycle?",
            'difficulty': 'medium',
            'options_en': ["Cycles through iterable infinitely", "List cycle", "String cycle", "Array cycle"],
            'options_uk': ["Нескінченно циклічно проходить ітерабельний", "Цикл списку", "Цикл рядка", "Цикл масиву"],
            'correct': 0,
        },
        {
            'text_en': "What is generator memory usage?",
            'text_uk': "Яке використання пам'яті генератором?",
            'difficulty': 'medium',
            'options_en': ["O(1) - constant memory", "O(n) - linear memory", "O(log n)", "O(n^2)"],
            'options_uk': ["O(1) - постійна пам'ять", "O(n) - лінійна пам'ять", "O(log n)", "O(n^2)"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_async_questions(topic):
    """20 questions for Async & Asyncio."""
    questions = [
        {
            'text_en': "What is async/await?",
            'text_uk': "Що таке async/await?",
            'difficulty': 'easy',
            'options_en': ["Syntax for async programming", "Decorator", "Module", "Class"],
            'options_uk': ["Синтаксис для асинхронного програмування", "Декоратор", "Модуль", "Клас"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio?",
            'text_uk': "Що таке asyncio?",
            'difficulty': 'easy',
            'options_en': ["Async I/O library", "Web framework", "Database", "Testing"],
            'options_uk': ["Бібліотека асинхронного вводу/виводу", "Веб фреймворк", "База даних", "Тестування"],
            'correct': 0,
        },
        {
            'text_en': "What is async def?",
            'text_uk': "Що таке async def?",
            'difficulty': 'easy',
            'options_en': ["Defines coroutine", "Regular function", "Class", "Decorator"],
            'options_uk': ["Визначає корутину", "Звичайна функція", "Клас", "Декоратор"],
            'correct': 0,
        },
        {
            'text_en': "What does await do?",
            'text_uk': "Що робить await?",
            'difficulty': 'easy',
            'options_en': ["Waits for coroutine completion", "Returns immediately", "Blocks thread", "Exits"],
            'options_uk': ["Чекає завершення корутини", "Повертає негайно", "Блокує потік", "Виходить"],
            'correct': 0,
        },
        {
            'text_en': "What is event loop?",
            'text_uk': "Що таке цикл подій?",
            'difficulty': 'medium',
            'options_en': ["Core of async - schedules coroutines", "Loop statement", "Iterator", "Generator"],
            'options_uk': ["Ядро асинхронності - планує корутини", "Оператор циклу", "Ітератор", "Генератор"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.gather()?",
            'text_uk': "Що таке asyncio.gather()?",
            'difficulty': 'medium',
            'options_en': ["Runs coroutines concurrently", "Sequential", "Single coroutine", "Error handler"],
            'options_uk': ["Запускає корутини конкурентно", "Послідовно", "Одна корутина", "Обробник помилок"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.run()?",
            'text_uk': "Що таке asyncio.run()?",
            'difficulty': 'easy',
            'options_en': ["Runs async function", "Creates loop", "Stops loop", "Pauses"],
            'options_uk': ["Запускає асинхронну функцію", "Створює цикл", "Зупиняє цикл", "Паузує"],
            'correct': 0,
        },
        {
            'text_en': "What is Task?",
            'text_uk': "Що таке Task?",
            'difficulty': 'medium',
            'options_en': ["Wrapped coroutine scheduled on loop", "Function", "Class", "Module"],
            'options_uk': ["Обгорнута корутина запланована на циклі", "Функція", "Клас", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.create_task()?",
            'text_uk': "Що таке asyncio.create_task()?",
            'difficulty': 'medium',
            'options_en': ["Schedules coroutine as Task", "Runs immediately", "Stops", "Pauses"],
            'options_uk': ["Планує корутину як Task", "Запускає негайно", "Зупиняє", "Паузує"],
            'correct': 0,
        },
        {
            'text_en': "Asyncio vs threading?",
            'text_uk': "Asyncio проти threading?",
            'difficulty': 'hard',
            'options_en': ["Asyncio single-threaded cooperative, threading preemptive", "Same", "Threading faster", "No difference"],
            'options_uk': ["Asyncio однопоточне кооперативне, threading витісняюче", "Однакові", "Threading швидший", "Немає різниці"],
            'correct': 0,
        },
        {
            'text_en': "Asyncio vs multiprocessing?",
            'text_uk': "Asyncio проти multiprocessing?",
            'difficulty': 'hard',
            'options_en': ["Asyncio for I/O bound, multiprocessing for CPU bound", "Same", "Multiprocessing faster", "No difference"],
            'options_uk': ["Asyncio для I/O задач, multiprocessing для CPU задач", "Однакові", "Multiprocessing швидший", "Немає різниці"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.sleep()?",
            'text_uk': "Що таке asyncio.sleep()?",
            'difficulty': 'easy',
            'options_en': ["Non-blocking sleep", "Blocking sleep", "Thread sleep", "Process sleep"],
            'options_uk': ["Неблокуючий сон", "Блокуючий сон", "Сон потоку", "Сон процесу"],
            'correct': 0,
        },
        {
            'text_en': "What is async with?",
            'text_uk': "Що таке async with?",
            'difficulty': 'medium',
            'options_en': ["Async context manager", "Sync context", "Loop", "Iterator"],
            'options_uk': ["Асинхронний контекстний менеджер", "Синхронний контекст", "Цикл", "Ітератор"],
            'correct': 0,
        },
        {
            'text_en': "What is async for?",
            'text_uk': "Що таке async for?",
            'difficulty': 'medium',
            'options_en': ["Async iteration", "Sync iteration", "Loop", "Iterator"],
            'options_uk': ["Асинхронна ітерація", "Синхронна ітерація", "Цикл", "Ітератор"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.Queue?",
            'text_uk': "Що таке asyncio.Queue?",
            'difficulty': 'medium',
            'options_en': ["Async FIFO queue", "List", "Stack", "Array"],
            'options_uk': ["Асинхронна FIFO черга", "Список", "Стек", "Масив"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.Lock?",
            'text_uk': "Що таке asyncio.Lock?",
            'difficulty': 'hard',
            'options_en': ["Async synchronization primitive", "Thread lock", "Process lock", "File lock"],
            'options_uk': ["Асинхронний примітив синхронізації", "Блокування потоку", "Блокування процесу", "Блокування файлу"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.Semaphore?",
            'text_uk': "Що таке asyncio.Semaphore?",
            'difficulty': 'hard',
            'options_en': ["Limits concurrent operations", "Lock", "Queue", "Event"],
            'options_uk': ["Обмежує конкурентні операції", "Блокування", "Черга", "Подія"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.Event?",
            'text_uk': "Що таке asyncio.Event?",
            'difficulty': 'hard',
            'options_en': ["Async signaling primitive", "Event loop", "Task", "Coroutine"],
            'options_uk': ["Асинхронний примітив сигналізації", "Цикл подій", "Task", "Корутина"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.wait_for()?",
            'text_uk': "Що таке asyncio.wait_for()?",
            'difficulty': 'hard',
            'options_en': ["Timeout for coroutine", "Wait all", "Wait any", "Cancel"],
            'options_uk': ["Таймаут для корутини", "Чекати все", "Чекати будь-яке", "Скасувати"],
            'correct': 0,
        },
        {
            'text_en': "What is asyncio.as_completed()?",
            'text_uk': "Що таке asyncio.as_completed()?",
            'difficulty': 'hard',
            'options_en': ["Yields tasks as they complete", "Wait all", "Wait any", "Cancel"],
            'options_uk': ["Повертає задачі по мірі завершення", "Чекати все", "Чекати будь-яке", "Скасувати"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_django_orm_questions(topic):
    """25 questions for Django ORM."""
    questions = [
        {
            'text_en': "What is QuerySet?",
            'text_uk': "Що таке QuerySet?",
            'difficulty': 'easy',
            'options_en': ["Lazy database query representation", "SQL query", "Database connection", "Model"],
            'options_uk': ["Ліниве представлення запиту до БД", "SQL запит", "З'єднання з БД", "Модель"],
            'correct': 0,
        },
        {
            'text_en': "When is QuerySet evaluated?",
            'text_uk': "Коли QuerySet обчислюється?",
            'difficulty': 'medium',
            'options_en': ["When iterated, sliced, or len() called", "On creation", "On filter", "Never"],
            'options_uk': ["Коли ітерується, slicing, або len() викликано", "При створенні", "При filter", "Ніколи"],
            'correct': 0,
        },
        {
            'text_en': "What is select_related?",
            'text_uk': "Що таке select_related?",
            'difficulty': 'medium',
            'options_en': ["JOIN for ForeignKey/OneToOne", "Separate queries", "No optimization", "Cache"],
            'options_uk': ["JOIN для ForeignKey/OneToOne", "Окремі запити", "Без оптимізації", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is prefetch_related?",
            'text_uk': "Що таке prefetch_related?",
            'difficulty': 'medium',
            'options_en': ["Separate query for ManyToMany/Reverse FK", "JOIN", "No optimization", "Cache"],
            'options_uk': ["Окремий запит для ManyToMany/Reverse FK", "JOIN", "Без оптимізації", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is N+1 problem?",
            'text_uk': "Що таке проблема N+1?",
            'difficulty': 'medium',
            'options_en': ["1 query for list + N for related objects", "N queries total", "1 query total", "No problem"],
            'options_uk': ["1 запит для списку + N для пов'язаних об'єктів", "N запитів всього", "1 зап��т всього", "Немає проблеми"],
            'correct': 0,
        },
        {
            'text_en': "How to fix N+1?",
            'text_uk': "Як виправити N+1?",
            'difficulty': 'medium',
            'options_en': ["Use select_related/prefetch_related", "More queries", "No fix", "Raw SQL"],
            'options_uk': ["Використати select_related/prefetch_related", "Більше запитів", "Немає виправлення", "Raw SQL"],
            'correct': 0,
        },
        {
            'text_en': "What is annotate()?",
            'text_uk': "Що таке annotate()?",
            'difficulty': 'hard',
            'options_en': ["Add calculated fields to queryset", "Filter", "Order", "Delete"],
            'options_uk': ["Додати обчислювані поля до queryset", "Filter", "Order", "Delete"],
            'correct': 0,
        },
        {
            'text_en': "What is aggregate()?",
            'text_uk': "Що таке aggregate()?",
            'difficulty': 'hard',
            'options_en': ["Calculate summary values", "Add fields", "Filter", "Order"],
            'options_uk': ["Обчислити підсумкові значення", "Додати поля", "Filter", "Order"],
            'correct': 0,
        },
        {
            'text_en': "What is F() expression?",
            'text_uk': "Що таке вираз F()?",
            'difficulty': 'hard',
            'options_en': ["Reference model field value", "Fixed value", "String", "Number"],
            'options_uk': ["Посилання на значення поля моделі", "Фіксоване значення", "Рядок", "Число"],
            'correct': 0,
        },
        {
            'text_en': "What is Q() object?",
            'text_uk': "Що таке об'єкт Q()?",
            'difficulty': 'hard',
            'options_en': ["Complex queries with AND/OR/NOT", "Simple filter", "Order", "Delete"],
            'options_uk': ["Складні запити з AND/OR/NOT", "Простий filter", "Order", "Delete"],
            'correct': 0,
        },
        {
            'text_en': "What is Manager?",
            'text_uk': "Що таке Manager?",
            'difficulty': 'medium',
            'options_en': ["Interface for database queries", "Model", "QuerySet", "Field"],
            'options_uk': ["Інтерфейс для запитів до БД", "Модель", "QuerySet", "Поле"],
            'correct': 0,
        },
        {
            'text_en': "What is custom Manager?",
            'text_uk': "Що таке кастомний Manager?",
            'difficulty': 'hard',
            'options_en': ["Custom query methods", "Default manager", "Model", "Field"],
            'options_uk': ["Кастомні методи запитів", "Менеджер за замовчуванням", "Модель", "Поле"],
            'correct': 0,
        },
        {
            'text_en': "What is get_or_create()?",
            'text_uk': "Що таке get_or_create()?",
            'difficulty': 'easy',
            'options_en': ["Get object or create if not exists", "Only get", "Only create", "Delete"],
            'options_uk': ["Отримати об'єкт або створити якщо немає", "Тільки отримати", "Тільки створити", "Видалити"],
            'correct': 0,
        },
        {
            'text_en': "What is update_or_create()?",
            'text_uk': "Що таке update_or_create()?",
            'difficulty': 'medium',
            'options_en': ["Update if exists or create", "Only update", "Only create", "Delete"],
            'options_uk': ["Оновити якщо існує або створити", "Тільки оновити", "Тільки створити", "Видалити"],
            'correct': 0,
        },
        {
            'text_en': "What is bulk_create()?",
            'text_uk': "Що таке bulk_create()?",
            'difficulty': 'medium',
            'options_en': ["Create multiple objects in one query", "One at a time", "Update", "Delete"],
            'options_uk': ["Створити кілька об'єктів в одному запиті", "По одному", "Оновити", "Видалити"],
            'correct': 0,
        },
        {
            'text_en': "What is bulk_update()?",
            'text_uk': "Що таке bulk_update()?",
            'difficulty': 'medium',
            'options_en': ["Update multiple objects in one query", "One at a time", "Create", "Delete"],
            'options_uk': ["Оновити кілька об'єктів в одному запиті", "По одному", "Створити", "Видалити"],
            'correct': 0,
        },
        {
            'text_en': "What is transaction.atomic()?",
            'text_uk': "Що таке transaction.atomic()?",
            'difficulty': 'hard',
            'options_en': ["Database transaction wrapper", "No transaction", "Query", "Model"],
            'options_uk': ["Обгортка транзакції БД", "Без транзакції", "Запит", "Модель"],
            'correct': 0,
        },
        {
            'text_en': "What is signals?",
            'text_uk': "Що таке сигнали?",
            'difficulty': 'hard',
            'options_en': ["Callbacks on model events", "Queries", "Models", "Fields"],
            'options_uk': ["Зворотні виклики на події моделі", "Запити", "Моделі", "Поля"],
            'correct': 0,
        },
        {
            'text_en': "What is pre_save signal?",
            'text_uk': "Що таке сигнал pre_save?",
            'difficulty': 'hard',
            'options_en': ["Before model save", "After save", "Before delete", "After delete"],
            'options_uk': ["Перед збереженням моделі", "Після збереження", "Перед видаленням", "Після видалення"],
            'correct': 0,
        },
        {
            'text_en': "What is post_save signal?",
            'text_uk': "Що таке сигнал post_save?",
            'difficulty': 'hard',
            'options_en': ["After model save", "Before save", "Before delete", "After delete"],
            'options_uk': ["Після збереження моделі", "Перед збереженням", "Перед видаленням", "Після видалення"],
            'correct': 0,
        },
        {
            'text_en': "What is Meta ordering?",
            'text_uk': "Що таке впорядкування Meta?",
            'difficulty': 'easy',
            'options_en': ["Default ordering for queryset", "No ordering", "Random", "By ID"],
            'options_uk': ["Впорядкування за замовчуванням для queryset", "Без впорядкування", "Випадкове", "За ID"],
            'correct': 0,
        },
        {
            'text_en': "What is Meta indexes?",
            'text_uk': "Що таке індекси Meta?",
            'difficulty': 'medium',
            'options_en': ["Database indexes for model", "Python indexes", "No indexes", "Query indexes"],
            'options_uk': ["Індекси БД для моделі", "Індекси Python", "Без індексів", "Індекси запиту"],
            'correct': 0,
        },
        {
            'text_en': "What is __str__ in model?",
            'text_uk': "Що таке __str__ в моделі?",
            'difficulty': 'easy',
            'options_en': ["String representation", "SQL query", "Field", "Method"],
            'options_uk': ["Рядкове представлення", "SQL запит", "Поле", "Метод"],
            'correct': 0,
        },
        {
            'text_en': "What is ForeignKey on_delete?",
            'text_uk': "Що таке ForeignKey on_delete?",
            'difficulty': 'medium',
            'options_en': ["What to do on related object delete", "No action", "Create", "Update"],
            'options_uk': ["Що робити при видаленні пов'язаного об'єкта", "Без дії", "Створити", "Оновити"],
            'correct': 0,
        },
        {
            'text_en': "What is CASCADE on_delete?",
            'text_uk': "Що таке CASCADE on_delete?",
            'difficulty': 'medium',
            'options_en': ["Delete related objects too", "No action", "Set null", "Protect"],
            'options_uk': ["Видалити пов'язані об'єкти теж", "Без дії", "Встановити null", "Захистити"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_drf_questions(topic):
    """20 questions for Django REST Framework."""
    questions = [
        {
            'text_en': "What is Serializer?",
            'text_uk': "Що таке Serializer?",
            'difficulty': 'easy',
            'options_en': ["Converts model to JSON and back", "Database query", "Model", "View"],
            'options_uk': ["Перетворює модель в JSON і назад", "Запит до БД", "Модель", "View"],
            'correct': 0,
        },
        {
            'text_en': "What is ModelSerializer?",
            'text_uk': "Що таке ModelSerializer?",
            'difficulty': 'easy',
            'options_en': ["Auto-generates serializer from model", "Manual serializer", "View", "Model"],
            'options_uk': ["Автоматично генерує serializer з моделі", "Ручний serializer", "View", "Модель"],
            'correct': 0,
        },
        {
            'text_en': "What is APIView?",
            'text_uk': "Що таке APIView?",
            'difficulty': 'easy',
            'options_en': ["Base class for API views", "Model", "Serializer", "Database"],
            'options_uk': ["Базовий клас для API views", "Модель", "Serializer", "База даних"],
            'correct': 0,
        },
        {
            'text_en': "What is GenericAPIView?",
            'text_uk': "Що таке GenericAPIView?",
            'difficulty': 'medium',
            'options_en': ["APIView with common functionality", "Basic APIView", "Model", "Serializer"],
            'options_uk': ["APIView із загальною функціональністю", "Базова APIView", "Модель", "Serializer"],
            'correct': 0,
        },
        {
            'text_en': "What is ViewSet?",
            'text_uk': "Що таке ViewSet?",
            'difficulty': 'medium',
            'options_en': ["Combines multiple views", "Single view", "Model", "Serializer"],
            'options_uk': ["Поєднує кілька views", "Один view", "Модель", "Serializer"],
            'correct': 0,
        },
        {
            'text_en': "What is Router?",
            'text_uk': "Що таке Router?",
            'difficulty': 'medium',
            'options_en': ["Auto-generates URLs for ViewSets", "Manual URLs", "Model", "Serializer"],
            'options_uk': ["Автоматично генерує URL для ViewSets", "Ручні URL", "Модель", "Serializer"],
            'correct': 0,
        },
        {
            'text_en': "What is authentication?",
            'text_uk': "Що таке authentication?",
            'difficulty': 'easy',
            'options_en': ["Verify user identity", "Authorization", "Serialization", "Validation"],
            'options_uk': ["Перевірка ідентичності користувача", "Авторизація", "Серіалізація", "Валідація"],
            'correct': 0,
        },
        {
            'text_en': "What is permission?",
            'text_uk': "Що таке permission?",
            'difficulty': 'easy',
            'options_en': ["Check if user can access", "Authentication", "Serialization", "Validation"],
            'options_uk': ["Перевірка чи користувач може отримати доступ", "Аутентифікація", "Серіалізація", "Валідація"],
            'correct': 0,
        },
        {
            'text_en': "What is TokenAuthentication?",
            'text_uk': "Що таке TokenAuthentication?",
            'difficulty': 'medium',
            'options_en': ["Auth via token in header", "Session auth", "Basic auth", "No auth"],
            'options_uk': ["Аутентифікація через токен в заголовку", "Session auth", "Basic auth", "Без auth"],
            'correct': 0,
        },
        {
            'text_en': "What is JWT authentication?",
            'text_uk': "Що таке JWT аутентифікація?",
            'difficulty': 'medium',
            'options_en': ["Auth via JSON Web Token", "Session auth", "Basic auth", "No auth"],
            'options_uk': ["Аутентифікація через JSON Web Token", "Session auth", "Basic auth", "Без auth"],
            'correct': 0,
        },
        {
            'text_en': "What is throttling?",
            'text_uk': "Що таке throttling?",
            'difficulty': 'medium',
            'options_en': ["Rate limiting for API", "No limiting", "Authentication", "Authorization"],
            'options_uk': ["Обмеження частоти для API", "Без обмеження", "Аутентифікація", "Авторизація"],
            'correct': 0,
        },
        {
            'text_en': "What is pagination?",
            'text_uk': "Що таке pagination?",
            'difficulty': 'easy',
            'options_en': ["Split results into pages", "No splitting", "Authentication", "Authorization"],
            'options_uk': ["Розбиття результатів на сторінки", "Без розбиття", "Аутентифікація", "Авторизація"],
            'correct': 0,
        },
        {
            'text_en': "What is PageNumberPagination?",
            'text_uk': "Що таке PageNumberPagination?",
            'difficulty': 'easy',
            'options_en': ["Pagination by page number", "Offset pagination", "Cursor pagination", "No pagination"],
            'options_uk': ["Пагінація за номером сторінки", "Offset пагінація", "Cursor пагінація", "Без пагінації"],
            'correct': 0,
        },
        {
            'text_en': "What is LimitOffsetPagination?",
            'text_uk': "Що таке LimitOffsetPagination?",
            'difficulty': 'medium',
            'options_en': ["Pagination by limit and offset", "Page number", "Cursor", "No pagination"],
            'options_uk': ["Пагінація за limit та offset", "Page number", "Cursor", "Без пагінації"],
            'correct': 0,
        },
        {
            'text_en': "What is CursorPagination?",
            'text_uk': "Що таке CursorPagination?",
            'difficulty': 'hard',
            'options_en': ["Pagination by cursor for large datasets", "Page number", "Limit offset", "No pagination"],
            'options_uk': ["Пагінація за курсором для великих наборів", "Page number", "Limit offset", "Без пагінації"],
            'correct': 0,
        },
        {
            'text_en': "What is filtering?",
            'text_uk': "Що таке фільтрація?",
            'difficulty': 'easy',
            'options_en': ["Select subset of results", "No selection", "Authentication", "Authorization"],
            'options_uk': ["Вибір підмножини результатів", "Без вибору", "Аутентифікація", "Авторизація"],
            'correct': 0,
        },
        {
            'text_en': "What is DjangoFilterBackend?",
            'text_uk': "Що таке DjangoFilterBackend?",
            'difficulty': 'medium',
            'options_en': ["Filter using Django query params", "No filtering", "Authentication", "Authorization"],
            'options_uk': ["Фільтрація через query params Django", "Без фільтрації", "Аутентифікація", "Авторизація"],
            'correct': 0,
        },
        {
            'text_en': "What is SearchFilter?",
            'text_uk': "Що таке SearchFilter?",
            'difficulty': 'medium',
            'options_en': ["Full-text search", "No search", "Authentication", "Authorization"],
            'options_uk': ["Повнотекстовий пошук", "Без пошуку", "Аутентифікація", "Авторизація"],
            'correct': 0,
        },
        {
            'text_en': "What is OrderingFilter?",
            'text_uk': "Що таке OrderingFilter?",
            'difficulty': 'medium',
            'options_en': ["Sort results by field", "No sorting", "Authentication", "Authorization"],
            'options_uk': ["Сортування результатів за полем", "Без сортування", "Аутентифікація", "Авторизація"],
            'correct': 0,
        },
        {
            'text_en': "What is validation in DRF?",
            'text_uk': "Що таке валідація в DRF?",
            'difficulty': 'medium',
            'options_en': ["Check data before save", "No check", "Authentication", "Authorization"],
            'options_uk': ["Перевірка даних перед збереженням", "Без перевірки", "Аутентифікація", "Авторизація"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_architecture_questions(topic):
    """20 questions for Python Architecture."""
    questions = [
        {
            'text_en': "What is WSGI?",
            'text_uk': "Що таке WSGI?",
            'difficulty': 'easy',
            'options_en': ["Web Server Gateway Interface", "Web Socket", "Database", "Cache"],
            'options_uk': ["Web Server Gateway Interface", "Web Socket", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is ASGI?",
            'text_uk': "Що таке ASGI?",
            'difficulty': 'easy',
            'options_en': ["Async Server Gateway Interface", "Sync only", "Database", "Cache"],
            'options_uk': ["Async Server Gateway Interface", "Тільки синхронний", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "WSGI vs ASGI?",
            'text_uk': "WSGI проти ASGI?",
            'difficulty': 'medium',
            'options_en': ["WSGI sync only, ASGI supports async", "Same", "ASGI sync only", "No difference"],
            'options_uk': ["WSGI тільки синхронний, ASGI підтримує async", "Однакові", "ASGI тільки синхронний", "Немає різниці"],
            'correct': 0,
        },
        {
            'text_en': "What is middleware?",
            'text_uk': "Що таке middleware?",
            'difficulty': 'easy',
            'options_en': ["Process request/response pipeline", "Database", "Cache", "Model"],
            'options_uk': ["Обробка конвеєра запит/відповідь", "База даних", "Кеш", "Модель"],
            'correct': 0,
        },
        {
            'text_en': "What is Celery?",
            'text_uk': "Що таке Celery?",
            'difficulty': 'medium',
            'options_en': ["Distributed task queue", "Web framework", "Database", "Cache"],
            'options_uk': ["Розподілена черга задач", "Веб фреймворк", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Redis?",
            'text_uk': "Що таке Redis?",
            'difficulty': 'easy',
            'options_en': ["In-memory data store/cache", "Database only", "Web server", "Framework"],
            'options_uk': ["Сховище/кеш в пам'яті", "Тільки база даних", "Веб сервер", "Фреймворк"],
            'correct': 0,
        },
        {
            'text_en': "What is message broker?",
            'text_uk': "Що таке брокер повідомлень?",
            'difficulty': 'medium',
            'options_en': ["Middleware for task queues", "Database", "Cache", "Web server"],
            'options_uk': ["Проміжне ПЗ для черг задач", "База даних", "Кеш", "Веб сервер"],
            'correct': 0,
        },
        {
            'text_en': "What is worker process?",
            'text_uk': "Що таке робочий процес?",
            'difficulty': 'medium',
            'options_en': ["Process that executes tasks", "Web process", "Database", "Cache"],
            'options_uk': ["Процес, який виконує задачі", "Веб процес", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is beat scheduler?",
            'text_uk': "Що таке планувальник beat?",
            'difficulty': 'hard',
            'options_en': ["Schedules periodic tasks", "Worker", "Broker", "Cache"],
            'options_uk': ["Планує періодичні задачі", "Worker", "Broker", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is SOLID?",
            'text_uk': "Що таке SOLID?",
            'difficulty': 'medium',
            'options_en': ["5 OOP design principles", "Database", "Cache", "Framework"],
            'options_uk': ["5 принципів проектування ООП", "База даних", "Кеш", "Фреймворк"],
            'correct': 0,
        },
        {
            'text_en': "What is Single Responsibility?",
            'text_uk': "Що таке Single Responsibility?",
            'difficulty': 'easy',
            'options_en': ["Class has one job", "Multiple jobs", "No jobs", "Database"],
            'options_uk': ["Клас має одну роботу", "Кілька робіт", "Без робіт", "База даних"],
            'correct': 0,
        },
        {
            'text_en': "What is Open/Closed?",
            'text_uk': "Що таке Open/Closed?",
            'difficulty': 'medium',
            'options_en': ["Open for extension, closed for modification", "Closed for both", "Open for both", "No principle"],
            'options_uk': ["Відкритий для розширення, закритий для модифікації", "Закритий для обох", "Відкритий для обох", "Немає принципу"],
            'correct': 0,
        },
        {
            'text_en': "What is Dependency Injection?",
            'text_uk': "Що таке Dependency Injection?",
            'difficulty': 'hard',
            'options_en': ["Pass dependencies instead of creating", "Create dependencies", "No dependencies", "Database"],
            'options_uk': ["Передавати залежності замість створення", "Створювати залежності", "Без залежностей", "База даних"],
            'correct': 0,
        },
        {
            'text_en': "What is Repository pattern?",
            'text_uk': "Що таке патерн Repository?",
            'difficulty': 'hard',
            'options_en': ["Abstraction over data access", "No abstraction", "Database", "Cache"],
            'options_uk': ["Абстракція над доступом до даних", "Без абстракції", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Service layer?",
            'text_uk': "Що таке шар Service?",
            'difficulty': 'hard',
            'options_en': ["Business logic layer", "Database", "Cache", "View"],
            'options_uk': ["Шар бізнес-логіки", "База даних", "Кеш", "View"],
            'correct': 0,
        },
        {
            'text_en': "What is DTO?",
            'text_uk': "Що таке DTO?",
            'difficulty': 'hard',
            'options_en': ["Data Transfer Object", "Database", "Cache", "View"],
            'options_uk': ["Data Transfer Object", "База даних", "Кеш", "View"],
            'correct': 0,
        },
        {
            'text_en': "What is CQRS?",
            'text_uk': "Що таке CQRS?",
            'difficulty': 'hard',
            'options_en': ["Command Query Responsibility Segregation", "No segregation", "Database", "Cache"],
            'options_uk': ["Command Query Responsibility Segregation", "Без розділення", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Event Sourcing?",
            'text_uk': "Що таке Event Sourcing?",
            'difficulty': 'hard',
            'options_en': ["Store state as events", "Store state as snapshot", "Database", "Cache"],
            'options_uk': ["Зберігати стан як події", "Зберігати стан як знімок", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Microservices?",
            'text_uk': "Що таке Мікросервіси?",
            'difficulty': 'medium',
            'options_en': ["Small independent services", "Monolith", "Database", "Cache"],
            'options_uk': ["Малі незалежні сервіси", "Моноліт", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is API Gateway?",
            'text_uk': "Що таке API Gateway?",
            'difficulty': 'medium',
            'options_en': ["Single entry point for APIs", "Multiple entry", "Database", "Cache"],
            'options_uk': ["Єдина точка входу для API", "Кілька входів", "База даних", "Кеш"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def seed_advanced_questions(topic):
    """20 questions for Advanced Python."""
    questions = [
        {
            'text_en': "What is metaclass?",
            'text_uk': "Що таке метаклас?",
            'difficulty': 'hard',
            'options_en': ["Class that creates classes", "Instance", "Object", "Module"],
            'options_uk': ["Клас, який створює класи", "Екземпляр", "Об'єкт", "Модуль"],
            'correct': 0,
        },
        {
            'text_en': "What is type hinting?",
            'text_uk': "Що таке type hinting?",
            'difficulty': 'easy',
            'options_en': ["Type annotations for code clarity", "No types", "Database", "Cache"],
            'options_uk': ["Анотації типів для ясності коду", "Без типів", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is mypy?",
            'text_uk': "Що таке mypy?",
            'difficulty': 'medium',
            'options_en': ["Static type checker", "Dynamic checker", "Database", "Cache"],
            'options_uk': ["Статичний перевіряльник типів", "Динамічний перевіряльник", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Protocol?",
            'text_uk': "Що таке Protocol?",
            'difficulty': 'hard',
            'options_en': ["Structural subtyping interface", "No interface", "Database", "Cache"],
            'options_uk': ["Інтерфейс структурної підтипизації", "Без інтерфейсу", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Generic?",
            'text_uk': "Що таке Generic?",
            'difficulty': 'hard',
            'options_en': ["Type parameter for classes/functions", "No type", "Database", "Cache"],
            'options_uk': ["Параметр типу для класів/функцій", "Без типу", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is contextlib?",
            'text_uk': "Що таке contextlib?",
            'difficulty': 'medium',
            'options_en': ["Utilities for context managers", "No utilities", "Database", "Cache"],
            'options_uk': ["Утиліти для контекстних менеджерів", "Без утиліт", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is @contextmanager?",
            'text_uk': "Що таке @contextmanager?",
            'difficulty': 'hard',
            'options_en': ["Create context manager from generator", "No manager", "Database", "Cache"],
            'options_uk': ["Створити контекстний менеджер з генератора", "Без менеджера", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is typing module?",
            'text_uk': "Що таке модуль typing?",
            'difficulty': 'medium',
            'options_en': ["Type hint support", "No types", "Database", "Cache"],
            'options_uk': ["Підтримка type hint", "Без типів", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Optional?",
            'text_uk': "Що таке Optional?",
            'difficulty': 'medium',
            'options_en': ["Type can be None", "Not None", "Database", "Cache"],
            'options_uk': ["Тип може бути None", "Не None", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Union?",
            'text_uk': "Що таке Union?",
            'difficulty': 'medium',
            'options_en': ["Type can be one of several", "Single type", "Database", "Cache"],
            'options_uk': ["Тип може бути одним з кількох", "Один тип", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is Callable?",
            'text_uk': "Що таке Callable?",
            'difficulty': 'hard',
            'options_en': ["Function type hint", "No function", "Database", "Cache"],
            'options_uk': ["Type hint для функції", "Без функції", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is TypedDict?",
            'text_uk': "Що таке TypedDict?",
            'difficulty': 'hard',
            'options_en': ["Dict with typed keys", "Regular dict", "Database", "Cache"],
            'options_uk': ["Словник з типізованими ключами", "Звичайний dict", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is NamedTuple?",
            'text_uk': "Що таке NamedTuple?",
            'difficulty': 'medium',
            'options_en': ["Tuple with named fields", "Regular tuple", "Database", "Cache"],
            'options_uk': ["Кортеж з іменованими полями", "Звичайний кортеж", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is dataclass?",
            'text_uk': "Що таке dataclass?",
            'difficulty': 'medium',
            'options_en': ["Decorator for boilerplate classes", "Regular class", "Database", "Cache"],
            'options_uk': ["Декоратор для шаблонних класів", "Звичайний клас", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is __post_init__?",
            'text_uk': "Що таке __post_init__?",
            'difficulty': 'hard',
            'options_en': ["Called after dataclass init", "Before init", "Database", "Cache"],
            'options_uk': ["Викликається після init dataclass", "Перед init", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is field() in dataclass?",
            'text_uk': "Що таке field() в dataclass?",
            'difficulty': 'hard',
            'options_en': ["Customize field behavior", "No customization", "Database", "Cache"],
            'options_uk': ["Налаштувати поведінку поля", "Без налаштування", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is ABC?",
            'text_uk': "Що таке ABC?",
            'difficulty': 'medium',
            'options_en': ["Abstract Base Class", "Concrete class", "Database", "Cache"],
            'options_uk': ["Абстрактний базовий клас", "Конкретний клас", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is @abstractmethod?",
            'text_uk': "Що таке @abstractmethod?",
            'difficulty': 'medium',
            'options_en': ["Must be implemented by subclass", "Optional", "Database", "Cache"],
            'options_uk': ["Має бути реалізовано підкласом", "Необов'язково", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is __annotations__?",
            'text_uk': "Що таке __annotations__?",
            'difficulty': 'hard',
            'options_en': ["Dict of type annotations", "No annotations", "Database", "Cache"],
            'options_uk': ["Словник анотацій типів", "Без анотацій", "База даних", "Кеш"],
            'correct': 0,
        },
        {
            'text_en': "What is get_type_hints()?",
            'text_uk': "Що таке get_type_hints()?",
            'difficulty': 'hard',
            'options_en': ["Get resolved type hints", "No hints", "Database", "Cache"],
            'options_uk': ["Отримати вирішені type hints", "Без hints", "База даних", "Кеш"],
            'correct': 0,
        },
    ]
    
    for q in questions:
        create_question(
            topic=topic,
            text_en=q['text_en'],
            text_uk=q['text_uk'],
            difficulty=q['difficulty'],
            options_en=q['options_en'],
            options_uk=q['options_uk'],
            correct_index=q['correct'],
            xp_reward=10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20
        )
    
    return len(questions)


def main():
    print("🐍 Seeding all Python questions...")
    
    # Create topics
    topics = get_or_create_topics()
    print(f"✓ Created {len(topics)} topics")
    
    # Seed questions for each topic
    total = 0
    
    print("\n📦 Python Basics...")
    count = seed_basics_questions(topics['basics'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n📦 OOP...")
    count = seed_oop_questions(topics['oop'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n🎨 Decorators...")
    count = seed_decorators_questions(topics['decorators'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n⚡ Generators...")
    count = seed_generators_questions(topics['generators'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n🚀 Async...")
    count = seed_async_questions(topics['async'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n🗄️ Django ORM...")
    count = seed_django_orm_questions(topics['django_orm'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n🔌 DRF...")
    count = seed_drf_questions(topics['drf'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n🏗️ Architecture...")
    count = seed_architecture_questions(topics['architecture'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print("\n🔥 Advanced...")
    count = seed_advanced_questions(topics['advanced'])
    print(f"  ✓ Created {count} questions")
    total += count
    
    print(f"\n✅ TOTAL: Created {total} questions across all Python topics!")
    return total


if __name__ == '__main__':
    main()
