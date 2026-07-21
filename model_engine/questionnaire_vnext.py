QUESTIONNAIRE_VNEXT_BLOCKS = {
    "KCog": [
        "KCog1", "KCog2", "KCog3", "KCog4",
        "KCog5", "KCog6", "KCog7",
    ],
    "MG": [
        "MG1", "MG2", "MG3", "MG4",
        "MG5", "MG6", "MG7",
    ],
    "PR": ["PR1", "PR2", "PR3", "PR4", "PR5", "PR6"],
    "SR": ["SR1", "SR2", "SR3", "SR4"],
    "FR": ["FR1", "FR2", "FR3", "FR4"],
    "MR": [
        "MR1", "MR2", "MR3", "MR4", "MR5",
        "MR6", "MR7", "MR8", "MR9",
    ],
    "RC": ["RC1", "RC2"],
    "MT": ["MT1", "MT2", "MT3", "MT4"],
    "RE": ["RE1", "RE2"],
    "PEP": ["PEP1", "PEP2"],
    "DR": ["DR1", "DR2", "DR3", "DR4", "DR5", "DR6", "DR7"],
    "Q": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10"],
}

VNEXT_CONSTRUCT_MAP = {
    "DecisionDegradation": [
        "KCog1", "KCog2", "KCog3", "KCog4",
        "KCog5", "KCog6", "KCog7",
        "MT1", "MT2", "MT3", "MT4",
        "DR5", "DR6", "DR7",
    ],

    "OptionSpaceCollapse": [
        "SR1", "FR1", "Q2", "Q3", "Q8",
    ],

    "ResourceExhaustionSignal": [
    "RE1",
    "RE2",
    "MT1",
    "MT2",
    "MT3",
    "Q10",
    ],

    "NegativeSpiral": [
    "Q5",
    "Q6",
    ],

    "HopelessnessSignal": {
    "questions": [
        "Q2",
        "Q3",
        "Q10",
    ],
    "type": "mean",
},

    "ControlGap": [
        "MG4", "SR2", "FR4",
    ],

    "RecoveryVulnerability": [
        "RE1", "RE2",
    ],

    "ResourceExhaustionSignal": [
        "RE1", "RE2", "MT1", "MT2", "MT3",
    ],

    "LearningFailure": [
        "DR1", "DR2", "DR4", "DR6",
    ],

    "CommitmentTrap": [
        "DR4", "MR2",
    ],

    "NegativeSpiral": [
        "Q6",
    ],

    "PEP": [
        "PEP1", "PEP2",
    ],
}

VNEXT_SIGNAL_GROUPS = {
    "DecisionDegradation": {
        "questions": [
            "KCog1", "KCog2", "KCog3", "KCog4",
            "KCog5", "KCog6", "KCog7",
            "MT1", "MT2", "MT3", "MT4",
            "DR5", "DR6", "DR7",
        ],
        "type": "mean",
    },

    "LearningFailure": {
        "questions": [
            "DR1", "DR2", "DR4", "DR6",
        ],
        "type": "mean",
    },

    "RecoveryVulnerability": {
        "questions": [
            "RE1", "RE2",
        ],
        "type": "mean",
    },

    "OptionSpaceCollapse": {
        "questions": [
            "SR1",
            "FR1",
            "Q2",
            "Q3",
            "Q8",
        ],
        "type": "mean",
    },

    "ResourceExhaustionSignal": {
        "questions": [
            "RE1",
            "RE2",
            "MT1",
            "MT2",
            "MT3",
            "Q10",
        ],
        "type": "mean",
    },

    "HopelessnessSignal": {
        "questions": [
            "Q2",
            "Q3",
            "Q10",
        ],
        "type": "mean",
    },

    "NegativeSpiral": {
        "questions": [
            "Q5",
            "Q6",
        ],
        "type": "mean",
    },

    "PEP": {
        "questions": [
            "PEP1",
            "PEP2",
        ],
        "type": "mean",
    },

    "CommitmentTrap": {
        "questions": [
            "MR2",
            "DR4",
        ],
        "type": "mean",
    },
}

VNEXT_QUESTION_TEXTS = {
    "KCog1": {
        "ru": "Когда позже вспоминаете ситуацию, в которой пришлось долго разбираться, насколько быстро вы обычно понимаете, что было самым важным?",
        "en": "When you later recall a situation you had to work through for a long time, how quickly do you usually understand what was most important?",
        "es": "Cuando recuerdas una situación que tuviste que analizar durante mucho tiempo, ¿qué tan rápido sueles entender qué era lo más importante?",
    },
"KCog2": {
        "ru": "Когда непонятно, почему что-то произошло, что вы обычно делаете?",
        "en": "When it is unclear why something happened, what do you usually do?",
        "es": "Cuando no está claro por qué ocurrió algo, ¿qué sueles hacer?",
    },
    "KCog3": {
        "ru": "Если появляются основания считать, что ваше мнение или решение могли быть ошибочными, что обычно происходит?",
        "en": "If there are reasons to think your opinion or decision may have been wrong, what usually happens?",
        "es": "Si aparecen razones para pensar que tu opinión o decisión pudo haber sido incorrecta, ¿qué suele pasar?",
    },
    "KCog4": {
        "ru": "Когда в уже понятной для вас ситуации появляется новая важная информация, что вы обычно делаете?",
        "en": "When new important information appears in a situation you already understood, what do you usually do?",
        "es": "Cuando aparece información nueva e importante en una situación que ya entendías, ¿qué sueles hacer?",
    },
    "KCog5": {
        "ru": "Если ситуация изменилась и первоначальный план перестал работать, что обычно происходит?",
        "en": "If the situation changes and the original plan stops working, what usually happens?",
        "es": "Si la situación cambia y el plan inicial deja de funcionar, ¿qué suele pasar?",
    },
    "KCog6": {
        "ru": "Перед тем как сделать окончательный вывод или принять решение, что вы обычно делаете?",
        "en": "Before making a final conclusion or decision, what do you usually do?",
        "es": "Antes de llegar a una conclusión final o tomar una decisión, ¿qué sueles hacer?",
    },
    "KCog7": {
        "ru": "Если на сложный вопрос долго не удаётся найти понятный ответ, что обычно происходит?",
        "en": "If you cannot find a clear answer to a difficult question for a long time, what usually happens?",
        "es": "Si durante mucho tiempo no encuentras una respuesta clara a una pregunta difícil, ¿qué suele pasar?",
    },
    "DR1": {
        "ru": "Если несколько попыток подряд не принесли желаемого результата, что обычно происходит?",
        "en": "If several attempts in a row do not bring the desired result, what usually happens?",
        "es": "Si varios intentos seguidos no dan el resultado deseado, ¿qué suele pasar?",
    },
    "RE1": {
        "ru": "После отдыха, выходных или периода, когда нагрузка становится меньше, насколько быстро силы и состояние возвращаются к привычному уровню?",
        "en": "After rest, weekends, or a period when the load becomes lighter, how quickly do your energy and state return to your usual level?",
        "es": "Después de descansar, de un fin de semana o de un período con menos carga, ¿qué tan rápido vuelven tu energía y tu estado a su nivel habitual?",
    },

"RE2": {
        "ru": "Если период повышенной нагрузки продолжается дольше, чем вы ожидали, что обычно происходит с восстановлением?",
        "en": "If a period of increased load lasts longer than expected, what usually happens to your recovery?",
        "es": "Si un período de mayor carga dura más de lo esperado, ¿qué suele pasar con tu recuperación?",
    },

    "Q6": {
        "ru": "Когда негативные события начинают следовать одно за другим, насколько часто возникает ощущение, что ситуация закручивается всё сильнее?",
        "en": "When negative events start following one after another, how often does it feel like the situation is spiraling further?",
        "es": "Cuando los eventos negativos empiezan a sucederse uno tras otro, ¿con qué frecuencia sientes que la situación se está intensificando en espiral?",
    },
    "PEP1": {
        "ru": "Когда в жизни происходит что-то неожиданное и незапланированное, чего вы обычно ожидаете дальше?",
        "en": "When something unexpected and unplanned happens in life, what do you usually expect next?",
        "es": "Cuando ocurre algo inesperado y no planificado en la vida, ¿qué sueles esperar después?",
    },
    "MR2": {
        "ru": "Если вы уже потеряли время, деньги, силы или другие важные ресурсы, а результат всё ещё не достигнут, что обычно происходит?",
        "en": "If you have already lost time, money, energy, or other important resources and the result has still not been achieved, what usually happens?",
        "es": "Si ya has perdido tiempo, dinero, energía u otros recursos importantes y aún no has logrado el resultado, ¿qué suele pasar?",
    },
"MT1": {
        "ru": "Бывает ли, что когда вы работаете уставшим, забываете что-то важное и это влияет на исход дела?",
        "en": "When you work while tired, do you forget something important and does it affect the outcome?",
        "es": "Cuando trabajas con cansancio, ¿olvidas algo importante y eso afecta el resultado?",
    },
"MT2": {
        "ru": "Когда вы уставший, насколько увеличивается желание поскорее закрыть неприятный, сложный или утомительный вопрос?",
        "en": "When you are tired, how much does the desire to close an unpleasant, difficult, or exhausting issue as quickly as possible increase?",
        "es": "Cuando estás cansado/a, ¿cuánto aumenta el deseo de cerrar cuanto antes un asunto desagradable, difícil o agotador?",
    },
    "MT3": {
        "ru": "Бывает ли, что когда вы устали, становится трудно отказаться от уже выбранного способа действий, даже если появляется более удачный вариант?",
        "en": "When you are tired, does it become difficult to abandon an already chosen course of action even if a better option appears?",
        "es": "Cuando estás cansado/a, ¿se vuelve difícil abandonar una forma de actuar ya elegida aunque aparezca una mejor opción?",
    },
    "MT4": {
        "ru": "Бывает ли, что вы не видите проблемы до тех пор, пока её последствия уже становятся заметными?",
        "en": "Does it happen that you do not notice a problem until its consequences have already become visible?",
        "es": "¿Te ocurre que no ves un problema hasta que sus consecuencias ya se vuelven visibles?",
    },

"DR1": {
        "ru": "Насколько часто вы возвращаетесь к решениям или действиям, о которых потом жалеете?",
        "en": "How often do you return to decisions or actions that you later regret?",
        "es": "¿Con qué frecuencia vuelves a decisiones o acciones de las que luego te arrepientes?",
    },
    "DR2": {
        "ru": "Если решение уже приводило к плохим последствиям, насколько вам удаётся изменить поведение в следующий раз?",
        "en": "If a decision has already led to bad consequences, how well can you change your behavior next time?",
        "es": "Si una decisión ya llevó a malas consecuencias, ¿qué tan bien logras cambiar tu comportamiento la próxima vez?",
    },
    "DR4": {
        "ru": "Если вы понимаете, что выбранный путь не приводит к желаемому результату, насколько вам легко изменить направление?",
        "en": "If you understand that the chosen path is not leading to the desired result, how easy is it for you to change direction?",
        "es": "Si entiendes que el camino elegido no lleva al resultado deseado, ¿qué tan fácil te resulta cambiar de dirección?",
    },
    "DR5": {
        "ru": "Когда ситуация становится напряжённой, что чаще происходит с вашими решениями?",
        "en": "When a situation becomes tense, what usually happens to your decisions?",
        "es": "Cuando una situación se vuelve tensa, ¿qué suele pasar con tus decisiones?",
    },
    "DR6": {
        "ru": "Когда вы понимаете, что прежний способ не помогает, насколько легко вам попробовать другой подход?",
        "en": "When you understand that the previous approach is not helping, how easy is it for you to try another approach?",
        "es": "Cuando entiendes que el método anterior no ayuda, ¿qué tan fácil te resulta probar otro enfoque?",
    },
    "DR7": {
        "ru": "Бывает ли, что вы выбираете краткое облегчение сейчас, хотя понимаете, что позже это может усложнить ситуацию?",
        "en": "Does it happen that you choose short-term relief now even though you understand it may make the situation harder later?",
        "es": "¿Te ocurre que eliges un alivio breve ahora aunque entiendas que después puede complicar la situación?",
    },
    "Q6": {
        "ru": "Бывает ли сейчас так, что одна проблема усиливает другую по кругу?",
        "en": "Does it currently happen that one problem reinforces another in a loop?",
        "es": "¿Ocurre actualmente que un problema refuerza a otro en un círculo?",
    },
    "PEP2": {
        "ru": "Это ощущение для вас скорее было давно свойственно или появилось из-за текущей ситуации?",
        "en": "Is this feeling something that has been typical for you for a long time, or did it appear because of the current situation?",
        "es": "¿Esta sensación ha sido típica en ti desde hace tiempo o apareció por la situación actual?",
    },
}


