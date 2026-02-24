"""
Seed script to create Python questions for all topics.
Generates 20-30 questions per topic with English and Ukrainian translations.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from learning.models import Topic, Question, AnswerOption

# Helper to create question with options
def create_question(topic, text_en, text_uk, difficulty, options_en, options_uk, 
                    correct_index=0, question_type='multiple_choice', 
                    explanation_en='', explanation_uk='', xp_reward=10):
    """
    Create a question with answer options.
    
    Args:
        topic: Topic instance
        text_en: Question text in English
        text_uk: Question text in Ukrainian
        difficulty: 'easy', 'medium', or 'hard'
        options_en: List of option texts in English
        options_uk: List of option texts in Ukrainian
        correct_index: Index of correct answer (0-based)
        question_type: 'multiple_choice' or 'true_false'
        explanation_en: Explanation in English
        explanation_uk: Explanation in Ukrainian
        xp_reward: XP points for correct answer
    """
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
        text=text_en,  # Default to English
        explanation_en=explanation_en,
        explanation_uk=explanation_uk,
        explanation=explanation_en
    )
    
    # Update text field to match the language version
    question.text = text_en
    question.explanation = explanation_en
    question.save()
    
    for i, (opt_en, opt_uk) in enumerate(zip(options_en, options_uk)):
        option = AnswerOption.objects.create(
            question=question,
            text_en=opt_en,
            text_uk=opt_uk,
            text=opt_en,  # Default to English
            is_correct=(i == correct_index),
            order=i
        )
        # Ensure text field is updated
        option.text = opt_en
        option.save()
    
    return question


def seed_python_questions():
    print("🐍 Seeding Python questions...")
    
    # Get or create topics
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
        print(f"  {'✓ Created' if created else '✓ Exists'} topic: {topic.name}")
    
    # ============== PYTHON BASICS ==============
    print("\n📦 Creating Python Basics questions...")
    topic = topics['basics']
    
    questions_basics = [
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
            'explanation_en': "Strings in Python are immutable - you cannot change them after creation",
            'explanation_uk': "Рядки в Python є незмінними - ви не можете змінити їх після створення"
        },
        {
            'text_en': "What is the output of `print(bool(0), bool(''), bool([]))`?",
            'text_uk': "Що виведе `print(bool(0), bool(''), bool([]))`?",
            'difficulty': 'easy',
            'options_en': ["False False False", "True True True", "False True False", "None None None"],
            'options_uk': ["False False False", "True True True", "False True False", "None None None"],
            'correct': 0,
            'explanation_en': "0, empty string, and empty list are all falsy values in Python",
            'explanation_uk': "0, порожній рядок і порожній список є falsy значеннями в Python"
        },
        {
            'text_en': "What is the difference between `is` and `==` in Python?",
            'text_uk': "Яка різниця між `is` та `==` в Python?",
            'difficulty': 'easy',
            'options_en': [
                "`is` checks identity, `==` checks equality",
                "`is` checks equality, `==` checks identity",
                "They are the same",
                "`is` is for strings only"
            ],
            'options_uk': [
                "`is` перевіряє тотожність, `==` перевіряє рівність",
                "`is` перевіряє рівність, `==` перевіряє тотожність",
                "Вони однакові",
                "`is` тільки для рядків"
            ],
            'correct': 0,
            'explanation_en': "`is` checks if two objects are the same object in memory, `==` checks if values are equal",
            'explanation_uk': "`is` перевіряє чи два об'єкти є одним об'єктом в пам'яті, `==` перевіряє чи значення рівні"
        },
        {
            'text_en': "What does `*args` and `**kwargs` mean?",
            'text_uk': "Що означають `*args` та `**kwargs`?",
            'difficulty': 'medium',
            'options_en': [
                "*args = tuple of positional args, **kwargs = dict of named args",
                "*args = list, **kwargs = dictionary",
                "*args and **kwargs are the same thing",
                "They only accept numeric arguments"
            ],
            'options_uk': [
                "*args = tuple позиційних аргументів, **kwargs = dict іменованих",
                "*args = список, **kwargs = словник",
                "*args і **kwargs одне й те саме",
                "Вони приймають тільки числові аргументи"
            ],
            'correct': 0,
            'explanation_en': "*args collects positional arguments as a tuple, **kwargs collects keyword arguments as a dictionary",
            'explanation_uk': "*args збирає позиційні аргументи як tuple, **kwargs збирає іменовані аргументи як словник"
        },
        {
            'text_en': "What is the output?\n```python\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)\n```",
            'text_uk': "Що виведе цей код?\n```python\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)\n```",
            'difficulty': 'medium',
            'options_en': ["[1, 2, 3, 4]", "[1, 2, 3]", "[1, 2, 3], [1, 2, 3, 4]", "Error"],
            'options_uk': ["[1, 2, 3, 4]", "[1, 2, 3]", "[1, 2, 3], [1, 2, 3, 4]", "Помилка"],
            'correct': 0,
            'explanation_en': "b = a creates a reference to the same list, not a copy. Modifying b also modifies a.",
            'explanation_uk': "b = a створює посилання на той самий список, а не копію. Змінюючи b, ми змінюємо і a."
        },
        {
            'text_en': "What is list comprehension?",
            'text_uk': "Що таке list comprehension?",
            'difficulty': 'medium',
            'options_en': [
                "A concise way to create lists",
                "A type of loop",
                "A function for lists",
                "A list method"
            ],
            'options_uk': [
                "Стислий спосіб створення списків",
                "Тип циклу",
                "Функція для списків",
                "Метод списку"
            ],
            'correct': 0,
            'explanation_en': "List comprehension is a concise way to create lists: [x for x in range(10)]",
            'explanation_uk': "List comprehension - це стислий спосіб створення списків: [x for x in range(10)]"
        },
        {
            'text_en': "What is the output?\n```python\ndef func(x=[]):\n    x.append(1)\n    return x\n\nprint(func())\nprint(func())\nprint(func())\n```",
            'text_uk': "Що виведе цей код?\n```python\ndef func(x=[]):\n    x.append(1)\n    return x\n\nprint(func())\nprint(func())\nprint(func())\n```",
            'difficulty': 'hard',
            'options_en': [
                "[1], [1, 1], [1, 1, 1]",
                "[1], [1], [1]",
                "[1, 1, 1], [1, 1, 1], [1, 1, 1]",
                "Error"
            ],
            'options_uk': [
                "[1], [1, 1], [1, 1, 1]",
                "[1], [1], [1]",
                "[1, 1, 1], [1, 1, 1], [1, 1, 1]",
                "Помилка"
            ],
            'correct': 0,
            'explanation_en': "Default mutable arguments are created once when the function is defined, not each time it's called",
            'explanation_uk': "Мутабельні аргументи за замовчуванням створюються один раз при визначенні функції, а не щоразу при виклику"
        },
        {
            'text_en': "What is `__slots__` in Python?",
            'text_uk': "Що таке `__slots__` в Python?",
            'difficulty': 'hard',
            'options_en': [
                "A way to restrict attributes and save memory",
                "A type of decorator",
                "A method for classes",
                "A way to create private variables"
            ],
            'options_uk': [
                "Спосіб обмежити атрибути та зекономити пам'ять",
                "Тип декоратора",
                "Метод для класів",
                "Спосіб створити приватні змінні"
            ],
            'correct': 0,
            'explanation_en': "__slots__ restricts allowed attributes and saves memory by preventing __dict__ creation",
            'explanation_uk': "__slots__ обмежує дозволені атрибути та економить пам'ять, запобігаючи створенню __dict__"
        },
        {
            'text_en': "What is GIL in Python?",
            'text_uk': "Що таке GIL в Python?",
            'difficulty': 'hard',
            'options_en': [
                "Global Interpreter Lock - limits to 1 thread executing Python bytecode at once",
                "Global Integration Library",
                "A package manager",
                "A testing framework"
            ],
            'options_uk': [
                "Global Interpreter Lock - обмежує до 1 потоку, що виконує Python байткод одночасно",
                "Global Integration Library",
                "Менеджер пакетів",
                "Фреймворк для тестування"
            ],
            'correct': 0,
            'explanation_en': "GIL is a mutex that allows only one thread to execute Python bytecode at a time in CPython",
            'explanation_uk': "GIL - це м'ютекс, який дозволяє тільки одному потоку виконувати Python байткод одночасно в CPython"
        },
        {
            'text_en': "What is the difference between deep and shallow copy?",
            'text_uk': "Яка різниця між глибоким та поверхневим копіюванням?",
            'difficulty': 'medium',
            'options_en': [
                "Shallow copy creates new object but references nested objects, deep copy copies everything recursively",
                "They are the same",
                "Deep copy is faster",
                "Shallow copy only works with lists"
            ],
            'options_uk': [
                "Shallow copy створює новий об'єкт, але посилається на вкладені, deep copy копіює все рекурсивно",
                "Вони однакові",
                "Deep copy швидший",
                "Shallow copy працює тільки зі списками"
            ],
            'correct': 0,
            'explanation_en': "Shallow copy creates new object but nested objects are shared. Deep copy creates independent copies of everything",
            'explanation_uk': "Shallow copy створює новий об'єкт, але вкладені об'єкти спільні. Deep copy створює незалежні копії всього"
        },
        {
            'text_en': "What does `__name__ == '__main__'` do?",
            'text_uk': "Що робить `__name__ == '__main__'`?",
            'difficulty': 'easy',
            'options_en': [
                "Checks if script is run directly vs imported",
                "Defines the main function",
                "Imports the main module",
                "Creates a new namespace"
            ],
            'options_uk': [
                "Перевіряє чи скрипт запущено безпосередньо, а не імпортовано",
                "Визначає головну функцію",
                "Імпортує головний модуль",
                "Створює новий простір імен"
            ],
            'correct': 0,
            'explanation_en': "It's True when the script is run directly, False when imported as a module",
            'explanation_uk': "Це True, коли скрипт запущено безпосередньо, False коли імпортовано як модуль"
        },
        {
            'text_en': "What is a lambda function?",
            'text_uk': "Що таке lambda функція?",
            'difficulty': 'easy',
            'options_en': [
                "An anonymous single-expression function",
                "A type of class",
                "A decorator",
                "A module"
            ],
            'options_uk': [
                "Анонімна функція з одним виразом",
                "Тип класу",
                "Декоратор",
                "Модуль"
            ],
            'correct': 0,
            'explanation_en': "Lambda is an anonymous function defined with 'lambda' keyword, can have any arguments but only one expression",
            'explanation_uk': "Lambda - це анонімна функція, визначена з ключовим словом 'lambda', може мати будь-які аргументи, але тільки один вираз"
        },
        {
            'text_en': "What is the output of `print(2 ** 3 ** 2)`?",
            'text_uk': "Що виведе `print(2 ** 3 ** 2)`?",
            'difficulty': 'medium',
            'options_en': ["512", "64", "72", "36"],
            'options_uk': ["512", "64", "72", "36"],
            'correct': 0,
            'explanation_en': "Exponentiation is right-associative: 2 ** (3 ** 2) = 2 ** 9 = 512",
            'explanation_uk': "Піднесення до степеня є правоасоціативним: 2 ** (3 ** 2) = 2 ** 9 = 512"
        },
        {
            'text_en': "What is `__init__` vs `__new__`?",
            'text_uk': "Що таке `__init__` проти `__new__`?",
            'difficulty': 'hard',
            'options_en': [
                "__new__ creates the instance, __init__ initializes it",
                "They are the same",
                "__init__ creates, __new__ initializes",
                "__new__ is for classes only"
            ],
            'options_uk': [
                "__new__ створює екземпляр, __init__ ініціалізує його",
                "Вони однакові",
                "__init__ створює, __new__ ініціалізує",
                "__new__ тільки для класів"
            ],
            'correct': 0,
            'explanation_en': "__new__ is a static method that creates and returns the instance, __init__ is an instance method that initializes it",
            'explanation_uk': "__new__ - це статичний метод, який створює і повертає екземпляр, __init__ - це метод екземпляра, який ініціалізує його"
        },
        {
            'text_en': "What is the purpose of `if __name__ == '__main__'`?",
            'text_uk': "Яке призначення `if __name__ == '__main__'`?",
            'difficulty': 'easy',
            'options_en': [
                "To allow code to run only when script is executed directly",
                "To import modules",
                "To define global variables",
                "To create classes"
            ],
            'options_uk': [
                "Щоб код виконувався тільки коли скрипт запущено безпосередньо",
                "Щоб імпортувати модулі",
                "Щоб визначити глобальні змінні",
                "Щоб створити класи"
            ],
            'correct': 0
        },
        {
            'text_en': "What is the difference between `range()` and a list?",
            'text_uk': "Яка різниця між `range()` та списком?",
            'difficulty': 'easy',
            'options_en': [
                "range() is lazy (generator-like), list stores all values in memory",
                "They are the same",
                "range() is faster",
                "list can only contain numbers"
            ],
            'options_uk': [
                "range() є лінивим (як генератор), список зберігає всі значення в пам'яті",
                "Вони однакові",
                "range() швидший",
                "список може містити тільки числа"
            ],
            'correct': 0,
            'explanation_en': "range() returns a range object that generates values on demand, while list stores all values in memory",
            'explanation_uk': "range() повертає об'єкт range, який генерує значення на вимогу, тоді як список зберігає всі значення в пам'яті"
        },
        {
            'text_en': "What does the `zip()` function do?",
            'text_uk': "Що робить функція `zip()`?",
            'difficulty': 'easy',
            'options_en': [
                "Combines multiple iterables element-wise",
                "Compresses data",
                "Sorts a list",
                "Filters elements"
            ],
            'options_uk': [
                "Поєднує кілька ітерабельних об'єктів поелементно",
                "Стискає дані",
                "Сортує список",
                "Фільтрує елементи"
            ],
            'correct': 0,
            'explanation_en': "zip() returns an iterator of tuples where the i-th tuple contains the i-th element from each input iterable",
            'explanation_uk': "zip() повертає ітератор кортежів, де i-й кортеж містить i-й елемент з кожного вхідного ітерабельного об'єкта"
        },
        {
            'text_en': "What is a set in Python?",
            'text_uk': "Що таке множина (set) в Python?",
            'difficulty': 'easy',
            'options_en': [
                "An unordered collection of unique elements",
                "An ordered list",
                "A type of dictionary",
                "A tuple with special methods"
            ],
            'options_uk': [
                "Невпорядкована колекція унікальних елементів",
                "Впорядкований список",
                "Тип словника",
                "Кортеж зі спеціальними методами"
            ],
            'correct': 0,
            'explanation_en': "A set is an unordered collection that automatically removes duplicates",
            'explanation_uk': "Множина - це невпорядкована колекція, яка автоматично видаляє дублікати"
        },
        {
            'text_en': "What is the output of `print('Python'[-3:])`?",
            'text_uk': "Що виведе `print('Python'[-3:])`?",
            'difficulty': 'medium',
            'options_en': ["hon", "Pyt", "tho", "n"],
            'options_uk': ["hon", "Pyt", "tho", "n"],
            'correct': 0,
            'explanation_en': "Negative indexing starts from the end, [-3:] gives last 3 characters",
            'explanation_uk': "Негативна індексація починається з кінця, [-3:] дає останні 3 символи"
        },
        {
            'text_en': "What is the difference between `append()` and `extend()`?",
            'text_uk': "Яка різниця між `append()` та `extend()`?",
            'difficulty': 'medium',
            'options_en': [
                "append() adds one element, extend() adds all elements from an iterable",
                "They are the same",
                "append() is faster",
                "extend() only works with tuples"
            ],
            'options_uk': [
                "append() додає один елемент, extend() додає всі елементи з ітерабельного",
                "Вони однакові",
                "append() швидший",
                "extend() працює тільки з кортежами"
            ],
            'correct': 0,
            'explanation_en': "append() adds its argument as a single element, extend() iterates over its argument and adds each element",
            'explanation_uk': "append() додає свій аргумент як один елемент, extend() ітерує свій аргумент і додає кожен елемент"
        },
        {
            'text_en': "What is `*` (unpacking) operator?",
            'text_uk': "Що таке оператор `*` (розпакування)?",
            'difficulty': 'medium',
            'options_en': [
                "Unpacks iterable into individual elements",
                "Multiplies values",
                "Creates a pointer",
                "Defines a decorator"
            ],
            'options_uk': [
                "Розпаковує ітерабельний об'єкт на окремі елементи",
                "Множить значення",
                "Створює вказівник",
                "Визначає декоратор"
            ],
            'correct': 0,
            'explanation_en': "* unpacks an iterable into individual elements, useful for function calls and list operations",
            'explanation_uk': "* розпаковує ітерабельний об'єкт на окремі елементи, корисно для викликів функцій та операцій зі списками"
        },
        {
            'text_en': "What is the purpose of `pass` statement?",
            'text_uk': "Яке призначення оператора `pass`?",
            'difficulty': 'easy',
            'options_en': [
                "A null operation - does nothing, used as placeholder",
                "Skips to next iteration",
                "Exits a loop",
                "Continues execution"
            ],
            'options_uk': [
                "Порожня операція - нічого не робить, використовується як заповнювач",
                "Переходить до наступної ітерації",
                "Виходить з циклу",
                "Продовжує виконання"
            ],
            'correct': 0,
            'explanation_en': "pass is a null statement used when a statement is syntactically required but no action is needed",
            'explanation_uk': "pass - це порожній оператор, який використовується, коли синтаксично потрібен оператор, але дія не потрібна"
        },
        {
            'text_en': "What is the difference between `sort()` and `sorted()`?",
            'text_uk': "Яка різниця між `sort()` та `sorted()`?",
            'difficulty': 'medium',
            'options_en': [
                "sort() modifies list in-place, sorted() returns new sorted list",
                "They are the same",
                "sort() is faster",
                "sorted() only works with numbers"
            ],
            'options_uk': [
                "sort() змінює список на місці, sorted() повертає новий відсортований список",
                "Вони однакові",
                "sort() швидший",
                "sorted() працює тільки з числами"
            ],
            'correct': 0,
            'explanation_en': "sort() is a list method that sorts in-place (returns None), sorted() is a built-in function that returns a new sorted list",
            'explanation_uk': "sort() - це метод списку, який сортує на місці (повертає None), sorted() - це вбудована функція, яка повертає новий відсортований список"
        },
        {
            'text_en': "What is a dictionary comprehension?",
            'text_uk': "Що таке dictionary comprehension?",
            'difficulty': 'medium',
            'options_en': [
                "A concise way to create dictionaries: {k: v for ...}",
                "A type of loop",
                "A dictionary method",
                "A way to iterate dictionaries"
            ],
            'options_uk': [
                "Стислий спосіб створення словників: {k: v for ...}",
                "Тип циклу",
                "Метод словника",
                "Спосіб ітерації словників"
            ],
            'correct': 0,
            'explanation_en': "Dictionary comprehension creates dictionaries in a concise way: {key: value for item in iterable}",
            'explanation_uk': "Dictionary comprehension створює словники стислим способом: {ключ: значення for елемент in ітерабельний}"
        },
    ]
    
    for q_data in questions_basics:
        create_question(
            topic=topic,
            text_en=q_data['text_en'],
            text_uk=q_data['text_uk'],
            difficulty=q_data['difficulty'],
            options_en=q_data['options_en'],
            options_uk=q_data['options_uk'],
            correct_index=q_data['correct'],
            question_type=q_data.get('question_type', 'multiple_choice'),
            explanation_en=q_data.get('explanation_en', ''),
            explanation_uk=q_data.get('explanation_uk', ''),
            xp_reward=10 if q_data['difficulty'] == 'easy' else 15 if q_data['difficulty'] == 'medium' else 20
        )
        print(f"  ✓ Created: {q_data['text_en'][:50]}...")
    
    print(f"\n✅ Created {len(questions_basics)} questions for Python Basics")
    
    return "Seed completed successfully!"


if __name__ == '__main__':
    result = seed_python_questions()
    print(f"\n{result}")
