"""IELTS Speaking question bank.

Sources:
    - Curated core: a verified deep-research pass over Cambridge IELTS 18/19/20,
      IELTS Liz, Keith Speaking Academy, Goat Guru, IELTS Juice.
    - Cambridge extractions: verbatim from Cambridge IELTS 4-17 PDFs
      (those with extractable text — books 4-8, 10-13, 17).

Bank shape:
    PART1_BANK: dict[str, list[str]]   — topic slug → 3-4 Q
    PART2_BANK: list[dict]             — cue cards with p3_key linking to PART3_THEMES
    PART3_THEMES: dict[str, list[tuple[str, list[str]]]]   — p3_key → list of (sub-theme, [Q])
    DEFAULT_PART3: fallback Part 3 when a cue card has no matching p3_key.
"""

from __future__ import annotations


PART1_BANK: dict[str, list[str]] = {
    "work_study": [
        "What do you do — work or study?",
        "What is your job?",
        "Why did you choose that job or subject?",
        "Do you enjoy your work or studies? Why?",
    ],
    "hometown": [
        "Where is your hometown?",
        "Tell me about the city where you live.",
        "What do you like most about your hometown?",
        "Has your hometown changed much since you were a child?",
    ],
    "home_accommodation": [
        "Do you live in a house or an apartment?",
        "Which is your favourite room in your home? Why?",
        "How long have you lived there?",
        "Would you like to move to a different home in the future?",
    ],
    "food": [
        "Can you find food from many different countries where you live?",
        "How often do you eat typical food from other countries?",
        "Have you ever tried making food from another country?",
        "What food from your country would you recommend to people from other countries?",
    ],
    "fruit": [
        "Which fruit do you enjoy eating the most?",
        "Are there any fruits that you prefer not to eat? Why?",
        "Do you like meals that include fruit as an ingredient?",
        "Where do you usually buy fresh fruit near your home?",
    ],
    "sleep": [
        "How many hours do you usually sleep at night?",
        "Do you sometimes sleep during the day?",
        "What do you do if you can't get to sleep at night?",
        "Do you ever remember the dreams you've had while you were asleep?",
    ],
    "museums": [
        "Did you enjoy going to museums when you were a child?",
        "Are there any interesting museums near where you live now?",
        "Do you think it is best to go to museums by yourself or with friends?",
        "When you visit another city or country, do you think it's important to go to a museum there?",
    ],
    "walking": [
        "How much walking do you do in your daily life?",
        "Do you prefer walking alone or with other people?",
        "Is there anywhere near where you live that is good for walking?",
        "Do you think people walk less than they did in the past? Why?",
    ],
    "weather": [
        "What's the weather usually like where you live?",
        "What kind of weather do you like best? Why?",
        "Does the weather affect what you do during the day?",
        "Do you prefer hot weather or cold weather?",
    ],
    "music": [
        "What kind of music do you usually listen to?",
        "Do you ever listen to live music?",
        "Has the kind of music you like changed since you were a child?",
        "Do you think it's important for children to learn an instrument?",
    ],
    "weekends": [
        "What do you usually do on weekends?",
        "Do you prefer to spend weekends with family or with friends?",
        "Are your weekends now different from when you were a child?",
        "What would be your ideal way to spend a weekend?",
    ],
    "shopping": [
        "Do you enjoy shopping?",
        "Do you prefer shopping online or in actual shops?",
        "How often do you go shopping for clothes?",
        "Has the way you shop changed in recent years?",
    ],
    "photos": [
        "Do you often take photos?",
        "Do you prefer taking photos of people or of places?",
        "Do you usually keep your photos on your phone or print them?",
        "When was the last time you took a photo that you really liked?",
    ],
    "friends": [
        "Do you have many friends?",
        "How often do you see your friends?",
        "Do you prefer to have a few close friends or many friends?",
        "Have you known any of your friends for a long time?",
    ],
    "technology": [
        "How much time do you spend on your phone each day?",
        "What apps do you use most often?",
        "Has technology changed the way you communicate with friends?",
        "Do you think people rely on technology too much?",
    ],
    "cam10_weekends": [
        "How do you usually spend your weekends? [Why?]",
        "Which is your favourite part of the weekend? [Why?]",
        "Do you think your weekends are long enough? [Why/Why not?]",
        "How important do you think it is to have free time at the weekends? [Why?]",
    ],
    "cam10_music": [
        "What types of music do you like to listen to? [Why?]",
        "At what times of day do you like to listen to music? [Why?]",
        "Did you learn to play a musical instrument when you were a child? [Why/Why not?]",
        "Do you think all children should learn to play a musical instrument? [Why/Why not?]",
    ],
    "cam10_travel": [
        "Do you enjoy travelling? [Why/Why not?]",
        "Have you done much travelling? [Why/Why not?]",
        "Do you think it’s better to travel alone or with other people? [Why?]",
        "Where would you like to travel in the future? [Why?]",
    ],
    "cam10_school": [
        "Did you go to secondary/high school near to where you lived? [Why/Why not?]",
        "What did you like about your secondary/high school? [Why?]",
        "Tell me about anything you didn’t like at your school.",
        "How do you think your school could be improved? [Why/Why not?]",
    ],
    "cam11_photographs": [
        "What type of photos do you like taking? [Why/Why not?]",
        "What do you do with photos you take? [Why/Why not?]",
        "When you visit other places, do you take photos or buy postcards? [Why/Why not?]",
        "Do you like people taking photos of you? [Why/Why not?]",
    ],
    "cam12_health": [
        "Is it important to you to eat healthy food? [Why?/Why not?]",
        "If you catch a cold, what do you do to help you feel better? [Why?]",
        "Do you pay attention to public information about health? [Why?/Why not?]",
        "What could you do to have a healthier lifestyle?",
    ],
    "cam12_songs_and_singing": [
        "Did you enjoy singing when you were younger? [Why?/Why not?]",
        "How often do you sing now? [Why?]",
        "Do you have a favourite song you like listening to? [Why?/Why not?]",
        "How important is singing in your culture? [Why?]",
    ],
    "cam12_clothes": [
        "Where do you buy most of your clothes? [Why?]",
        "How often do you buy new clothes for your self? [Why?]",
        "How do you decide which clothes to buy? [Why?]",
        "Have the kinds of clothes you like changed in recent years? [Why?/Why not?]",
    ],
    "cam12_art": [
        "Did you enjoy doing art lessons when you were a child? [Why?/Why not?]",
        "Do you ever draw or paint pictures now? [Why?/Why not?]",
        "When was the last time you went to an art gallery or exhibition? [Why?]",
        "What kind of pictures do you like having in your home? [Why?]",
    ],
    "cam13_television_programmes": [
        "Where do you usually watch TV programmes/shows? [Why?/Why not?]",
        "What’s your favourite TV programme/show? [Why?]",
        "Are there any programmes/shows you don't like watching? [Why?/Why not?]",
        "Do you think you will watch more TV or fewer TV programmes/shows in the future?",
    ],
    "cam13_age": [
        "Are you happy to be the age you are now? [Why/Why not?]",
        "When you were a child, did you think a lot about your future? [Why/Why not?]",
        "Do you think you have changed as you have got older? [Why/Why not?]",
        "What will be different about your life in the future? [Why]",
    ],
    "cam13_money": [
        "When you go shopping, do you prefer to pay for things in cash or by card? [Why?]",
        "Do you ever save money to buy special things? [Why/Why not?]",
        "Would you ever take a job which had low pay? [Why/Why not?]",
        "Would winning a lot of money make a big difference to your life? [Why/Why not?]",
    ],
    "cam13_animals": [
        "Are there many animals or birds where you live? [Why/Why not?]",
        "How often do you watch programmes or read articles about wild animals? [Why?]",
        "Have you ever been to a zoo or a wildlife park? [Why/Why not?]",
        "Would you like to have a job working with animals? [Why/Why not?]",
    ],
    "cam14_future": [
        "What job would you like to have ten years from now? [Why?]",
        "How useful will English be for your future? [Why/Why not?]",
        "How much travelling do you hope to do in the future? [Why/Why not?]",
        "How do you think your life will change in the future? [Why/Why not?]",
    ],
    "cam14_social_media": [
        "Which social media websites do you use?",
        "How much time do you spend on social media sites? [Why/Why not?]",
        "What kind of information about your self have you put on social media? [Why/Why not?]",
        "Is there anything you don't like about social media? [Why?]",
    ],
    "cam14_neighbours": [
        "How often do you see your neighbours? [Why/Why not?]",
        "Do you invite your neighbours to your home? [Why/Why not?]",
        "Do you think you are a good neighbour? [Why/Why not?]",
        "Has a neighbour ever helped you? [Why/Why not?]",
    ],
    "cam14_your_neighbourhood": [
        "Do you like the neighbourhood you live in? [Why/Why not?]",
        "What do you do in your neighbourhood in your free time? [Why/Why not?]",
        "What new things would you like to have in your neighbourhood? [Why/Why not?]",
        "Would you like to live in another neighbourhood in your town or city? [Why/Why not?]",
    ],
    "cam15_email": [
        "What kinds of emails do you receive about your work or studies?",
        "Do you prefer to email, phone or text your friends? [Why?]",
        "Do you reply to emails and messages as soon as you receive them? [Why/Why not?]",
        "Are you happy to receive emails that are advertising things? [Why/Why not?]",
    ],
    "cam15_languages": [
        "How many languages can you speak? [Why/Why not?]",
        "How useful will English be to you in your future? [Why/Why not?]",
        "What do you remember about learning languages at school? [Why/Why not?]",
        "What do you think would be the hardest language for you to learn? [Why?]",
    ],
    "cam15_swimming": [
        "Did you learn to swim when you were a child? [Why/Why not?]",
        "How often do you go swimming now? [Why/Why not?]",
        "What places are there for swimming where you live? [Why?]",
        "Do you think it would be more enjoyable to go swimming outdoors or at an indoor pool? [Why?]",
    ],
    "cam15_jewellery": [
        "How often do you wear jewellery? [Why/Why not?]",
        "What type of jewellery do you like best? [Why/Why not?]",
        "When do people like to give jewellery in your country? [Why/Why not?]",
        "Have you ever given jewellery to someone as a gift? [Why/Why not?]",
    ],
    "cam16_people_you_study_work_with": [
        "Who do you spend most time studying/working with? [Why?]",
        "What kinds of things do you study/work on with other people? [Why?]",
        "Are there times when you study/work better by your self? [Why/Why not?]",
        "Is it important to like the people you study/work with? [Why/Why not?]",
    ],
    "cam16_flowers_and_plants": [
        "Do you have a favourite flower or plant? [Why/Why not?]",
        "What kinds of flowers and plants grow near where you live? [Why/Why not?]",
        "Is it important to you to have flowers and plants in your home? [Why/Why not?]",
        "Have you ever bought flowers for someone else? [Why/Why not?]",
    ],
    "cam16_summer": [
        "Is summer your favourite time of year? [Why/Why not?]",
        "What do you do in summer when the weather's very hot? [Why?]",
        "Do you go on holiday every summer? [Why/Why not?]",
        "Did you enjoy the summer holidays when you were at school? [Why/Why not?]",
    ],
    "cam16_fast_food": [
        "What kinds of fast food have you tried? [Why/Why not?]",
        "Do you ever use a microwave to cook food quickly? [Why/Why not?]",
        "How popular are fast food restaurants where you live? [Why/Why not?]",
        "When would you go to a fast-food restaurant? [Why/Why not?]",
    ],
    "cam17_history": [
        "What did you study in history lessons when you were at school?",
        "Did you enjoy studying history at school? [Why/Why not?]",
        "How often do you watch TV programmes about history now? [Why/Why not?]",
        "What period in history would you like to learn more about? [Why?]",
    ],
    "cam17_reading": [
        "Did you have a favourite book when you were a child? [Why/Why not?]",
        "How much reading do you do for your work/studies? [Why/Why not?]",
        "What kinds of books do you read for pleasure? [Why/Why not?]",
        "Do you prefer to read a newspaper or a magazine online, or to buy a copy? [Why?]",
    ],
    "cam17_drinks": [
        "What do you like to drink with your dinner? [Why?]",
        "Do you drink a lot of water every day? [Why/Why not?]",
        "Do you prefer drinking tea or coffee? [Why?]",
        "If people visit you in your home, what do you usually offer them to drink?",
    ],
    "cam17_maps": [
        "Do you think it’s better to use a paper map or a map on your phone? [Why?]",
        "When was the last time you needed to use a map? [Why/Why not?]",
        "If you visit a new city, do you always use a map to find your way around?",
        "In general, do you find it easy to read maps? [Why/Why not?]",
    ],
    "cam18_paying_bills": [
        "What kinds of bills do you have to pay?",
        "How do you usually pay your bills – in cash or by another method? [Why?]",
        "Have you ever forgotten to pay a bill? [Why/Why not?]",
        "Is there anything you could do to make your bills cheaper? [Why/Why not?]",
    ],
    "cam18_science": [
        "Did you like studying science when you were at school? [Why/Why not?]",
        "What do you remember about your science teachers at school?",
        "How interested are you in science now? [Why/Why not?]",
        "What do you think has been an important recent scientific development? [Why?]",
    ],
    "cam18_online_shopping": [
        "How often do you buy things online? [Why?]",
        "What was the last thing you bought online?",
        "Do you ever see things in shops and then buy them online? [Why/Why not?]",
        "Do you think the popularity of online shopping is changing your town or city centre? [Why/Why not?]",
    ],
    "cam18_sleep": [
        "How many hours do you usually sleep at night?",
        "Do you sometimes sleep during the day? [Why/Why not?]",
        "What do you do if you can't get to sleep at night? [Why?]",
        "Do you ever remember the dreams you've had while you were asleep?",
    ],
    "cam4_friends": [
        "Are your friends mostly your age or different ages? [Why?]",
        "Do you usually see your friends during the week or at weekends? [Why?]",
        "The last time you saw your friends, what did you do together?",
        "In what ways are your friends important to you?",
    ],
    "cam4_food_and_cooking": [
        "What kinds of food do you like to eat?",
        "What kind of new food would you like to try? [Why?]",
        "Do you like cooking? [Why/Why not?]",
        "What was the last meal you cooked?",
    ],
    "cam4_your_favourite_place": [
        "What place do you most like to visit?",
        "How often do you visit this place?",
        "Why do you like it so much?",
        "Is it popular with many other people?",
    ],
    "cam5_your_country": [
        "Which part of your country do most people live in?",
        "Tell me about the main industries there.",
        "How easy is it to travel around your country?",
        "Has your country changed much since you were a child?",
    ],
    "cam5_colour": [
        "What's your favourite colour? [Why?]",
        "Do you like the same colours now as you did when you were younger? (Why/Why not?]",
        "What can you learn about a person from the colours they like?",
        "Do any colours have a special meaning in your culture?",
    ],
    "cam5_entertainment": [
        "Do you prefer relaxing at home or going out in the evening? [Why?]",
        "When you go out for an evening, what do you like to do?",
        "How popular is this with other people in your country?",
        "Is there any kind of entertainment you do not like? [Why/Why not?]",
    ],
    "cam5_clothes": [
        "How important are clothes and fashion to you? [Why/Why not?]",
        "What kind of clothes do you dislike? [Why?]",
        "How different are the clothes you wear now from those you wore 10 years ago?",
        "What do you think the clothes we wear say about us?",
    ],
    "cam6_dancing": [
        "Do you enjoy dancing? (Why/Why not?]",
        "Has anyone ever taught you to dance? [Why/Why not?]",
        "Tell me about any traditional dancing in your country.",
        "Do you think that traditional dancing will be popular in the future? [Why/Why not?]",
    ],
    "cam6_musical_instruments": [
        "Which instrument do you like listening to most? [Why?]",
        "Have you ever learned to play a musical instrument? [Which one?]",
        "Do you think children should learn to play a musical instrument at school? [Why/Why not?]",
        "How easy would it be to learn to play an instrument without a teacher? [Why?]",
    ],
    "cam6_traffic_where_you_live": [
        "How do most people travel to work where you live?",
        "What traffic problems are there in your area? [Why?]",
        "How do traffic problems affect you?",
        "How would you reduce the traffic problems in your area?",
    ],
    "cam6_your_friends": [
        "Do you prefer to have one particular friend or a group of friends? [Why?]",
        "What do you like doing most with your friend/s?",
        "Do you think it's important to keep in coatact with friends you knew as a child?",
        "What makes a friend into a good friend?",
    ],
    "cam7_keeping_in_contact_with_people": [
        "How do you usually contact your friends? [Why?]",
        "Do you prefer to contact different people in different ways? [Why?]",
        "Do you find it easy to keep in contact with friends and family? [Why/Why not?]",
        "In your country, did people in the past keep in contact in the same ways as they do today?",
    ],
    "cam7_laughing": [
        "What kinds of thing make you laugh?",
        "Do you like making other people laugh? [Why/Why not?]",
        "Do you think it's important for people to laugh? [Why/Why not?]",
        "Is laughing the same as feeling happy, do you think? [Why/Why not?]",
    ],
    "cam7_cold_weather": [
        "Have you ever been in very cold weather? [When?]",
        "How often is the weather cold where you come from?",
        "Are some parts of your country colder than others? [Why?]",
        "Would you prefer to live in a hot place or a cold place? [Why?]",
    ],
    "cam7_travelling_to_work_or_college": [
        "How do you usually travel to work or college? [Why?]",
        "Have you always travelled to work/college in the same way? [Why/Why not?]",
        "What do you like about travelling to work/college this way?",
        "What changes would improve the way you travel to work/college? (Why?]",
    ],
    "cam8_neighbours": [
        "How well do you know the people who live next door to you?",
        "How often do you see them? [Why/Why not?]",
        "What kinds of problem do people sometimes have with their neighbours?",
        "How do you think neighbours can help each other?",
    ],
    "cam8_newspapers_and_magazines": [
        "Which magazines and newspapers do you read? [Why?]",
        "What kinds of article are you most interested in? [Why?]",
        "Have you ever read a newspaper or magazine in a foreign language? [When/Why?]",
    ],
    "cam8_flowers": [
        "Do you like to have flowers in your home? [Why/Why not?]",
        "Where would you go to buy flowers? [Why?]",
        "On what occasions would you give someone flowers?",
        "Are flowers important in your culture? [Why/Why not?]",
    ],
    "cam8_television": [
        "How often do you watch television? [Why/Why not?]",
        "Which television channel do you usually watch? [Why?]",
        "Do you enjoy the advertisements on television? [Why/Why not?]",
        "Do you think most programmes on television are good? [Why/Why not?]",
    ],
    "cam9_games": [
        "What games are popular in your country? [Why?]",
        "Do you play any games? [Why/Why not?]",
        "How do people learn to play games in your country?",
        "Do you think it's important for people to play games? [Why/Why not?]",
    ],
    "cam9_giving_gifts": [
        "When do people give gifts or presents in your country?",
        "Do you ever take a gift when you visit someone in their home? [Why/Why not?]",
        "When did you last receive a gift? [What was it?]",
        "Do you enjoy looking for gifts for people? [Why/Why not?]",
    ],
    "cam9_telephoning": [
        "How often do you make telephone calls? [Why/Why not?]",
        "Who do you spend most time talking to on the telephone? [Why?]",
        "When do you think you'll next make a telephone call? [Why?]",
        "Do you sometimes prefer to send a text message instead of telephoning? [Why/Why not?]",
    ],
    "cam9_bicycles": [
        "How popular are bicycles in your home town? [Why?]",
        "How often do you ride a bicycle? [Why/Why not?]",
        "Do you think that bicycles are suitable for all ages? [Why/Why not?]",
        "What are the advantages of a bicycle compared to a car? [Why?]",
    ],
}


PART2_BANK: list[dict] = [
    {
        "topic": "a person you admire",
        "bullets": [
            "who this person is",
            "how you know them",
            "what qualities they have",
        ],
        "explain": "why you admire this person",
        "p3_key": "person_admire",
    },
    {
        "topic": "a memorable journey you have taken",
        "bullets": [
            "where you went",
            "who you went with",
            "what you did during the journey",
        ],
        "explain": "why this journey was memorable for you",
        "p3_key": "memorable_journey",
    },
    {
        "topic": "a useful skill you learned",
        "bullets": [
            "what the skill is",
            "when and where you learned it",
            "how you learned it",
        ],
        "explain": "why this skill has been useful for you",
        "p3_key": "useful_skill",
    },
    {
        "topic": "a situation when you had to adjust your original plans unexpectedly",
        "bullets": [
            "what your initial plans were",
            "what caused you to change them",
            "what new arrangements you made",
        ],
        "explain": "how you felt about having to make these changes",
        "p3_key": "changed_plan",
    },
    {
        "topic": "a book you have recently read",
        "bullets": [
            "what kind of book it is",
            "what it is about",
            "what sort of people would enjoy it",
        ],
        "explain": "why you liked it",
        "p3_key": "book_read",
    },
    {
        "topic": "a film you would like to watch again",
        "bullets": [
            "what the film is",
            "when you first saw it",
            "who you would watch it with",
        ],
        "explain": "why you would like to watch it again",
        "p3_key": "film_again",
    },
    {
        "topic": "a foreign country you would like to visit",
        "bullets": [
            "which country it is",
            "how you first heard about it",
            "what you would do there",
        ],
        "explain": "why you would like to visit this country",
        "p3_key": "foreign_country",
    },
    {
        "topic": "an important decision you made",
        "bullets": [
            "what the decision was",
            "when and where you made it",
            "what the result of the decision was",
        ],
        "explain": "why this decision was important to you",
        "p3_key": "important_decision",
    },
    {
        "topic": "a place you like to spend time in",
        "bullets": [
            "where this place is",
            "how often you go there",
            "what you do there",
        ],
        "explain": "why you like spending time there",
        "p3_key": "place_to_spend_time",
    },
    {
        "topic": "a piece of work you felt satisfied with",
        "bullets": [
            "what the work was",
            "when you did it",
            "how you did it",
        ],
        "explain": "why you felt satisfied with this piece of work",
        "p3_key": "satisfying_work",
    },
    {
        "topic": "some food or drink that you learned to prepare",
        "bullets": [
            "what food or drink it is",
            "when and how you learned to prepare it",
            "who taught you to prepare it",
        ],
        "explain": "how you felt when you first prepared it",
        "p3_key": "food_prepared",
    },
    {
        "topic": "a law that was introduced in your country and that you thought was a very good idea",
        "bullets": [
            "what the law was",
            "who introduced it",
            "when and why it was introduced",
        ],
        "explain": "why you thought this law was such a good idea",
        "p3_key": "good_law",
    },
    {
        "topic": "someone you know who does something well",
        "bullets": [
            "who this person is",
            "how you know this person",
            "what they do well",
        ],
        "explain": "why you think this person is so good at doing this",
        "p3_key": "cam10_someone_you_know_who_does_some",
    },
    {
        "topic": "a shop near where you live that you sometimes use",
        "bullets": [
            "what sorts of product or service it sells",
            "what the shop looks like",
            "where it is located",
        ],
        "explain": "why you use this shop",
        "p3_key": "cam10_a_shop_near_where_you_live_tha",
    },
    {
        "topic": "something you don’t have now but would really like to own in the future",
        "bullets": [
            "what this thing is",
            "how long you have wanted to own it",
            "where you first saw it",
        ],
        "explain": "why you would like to own it",
        "p3_key": "cam10_something_you_don_t_have_now_b",
    },
    {
        "topic": "a house/apartment that someone you know lives in",
        "bullets": [
            "whose house/apartment this is",
            "where the house/apartment is",
            "what it looks like inside",
        ],
        "explain": "what you like or dislike about this person’s house/apartment",
        "p3_key": "cam11_a_house_apartment_that_someone",
    },
    {
        "topic": "a writer you would like to meet",
        "bullets": [
            "who the writer is",
            "what you know about this writer already",
            "what you would like to find out about",
        ],
        "explain": "why you would like to meet this writer",
        "p3_key": "cam11_a_writer_you_would_like_to_mee",
    },
    {
        "topic": "an occasion when you had to wait a long time for someone or something to arrive",
        "bullets": [
            "who or what you were waiting for",
            "how long you had to wait",
            "why you had to wait a long time",
        ],
        "explain": "how you felt about waiting a long time",
        "p3_key": "cam12_an_occasion_when_you_had_to_wa",
    },
    {
        "topic": "a film/movie actor from your country who is very popular",
        "bullets": [
            "who this actor is",
            "what kinds of films/movies he/she acts in",
            "what you know about this actor's life",
        ],
        "explain": "why this actor is so popular",
        "p3_key": "cam12_a_film_movie_actor_from_your_c",
    },
    {
        "topic": "an interesting discussion you had about how you spend your money",
        "bullets": [
            "who you had the discussion with",
            "why you discussed this topic",
            "what the result of the discussion was",
        ],
        "explain": "why this discussion was interesting for you",
        "p3_key": "cam12_an_interesting_discussion_you_",
    },
    {
        "topic": "a time when you visited a friend or family member at their workplace",
        "bullets": [
            "who you visited",
            "where this person worked",
            "why you visited this person's",
        ],
        "explain": "how you felt about visiting this person's workplace",
        "p3_key": "cam12_a_time_when_you_visited_a_frie",
    },
    {
        "topic": "someone you know who has started a business",
        "bullets": [
            "who this person is",
            "what work this person does",
            "why this person decided to start a business",
        ],
        "explain": "whether you would like to do the same kind of work as this person",
        "p3_key": "cam13_someone_you_know_who_has_start",
    },
    {
        "topic": "a time when you started using a new technological device (e.g. a new computer or phone)",
        "bullets": [
            "what device you started using",
            "why you started using this device",
            "how easy or difficult it was to use",
        ],
        "explain": "how helpful this device was to you",
        "p3_key": "cam13_a_time_when_you_started_using_",
    },
    {
        "topic": "an interesting discussion you had as part of your work or studies",
        "bullets": [
            "what the subject of the discussion was",
            "who you discussed the subject with",
            "what opinions were expressed",
        ],
        "explain": "why you found the discussion interesting",
        "p3_key": "cam13_an_interesting_discussion_you_",
    },
    {
        "topic": "a website you use that helps you a lot in your work or studies",
        "bullets": [
            "what the website is",
            "how often you use the website",
            "what information the website gives you",
        ],
        "explain": "how your work or studies would change if this website didn’t exist",
        "p3_key": "cam13_a_website_you_use_that_helps_y",
    },
    {
        "topic": "a book that you enjoyed reading because you had to think a lot",
        "bullets": [
            "what this book was",
            "why you decided to read it",
            "what reading this book made you think about",
        ],
        "explain": "why you enjoyed reading this book",
        "p3_key": "cam14_a_book_that_you_enjoyed_readin",
    },
    {
        "topic": "something you liked very much which you bought for your home",
        "bullets": [
            "what you bought",
            "when and where you bought it",
            "why you chose this particular thing",
        ],
        "explain": "why you liked it so much",
        "p3_key": "cam14_something_you_liked_very_much_",
    },
    {
        "topic": "a very difficult task that you succeeded in doing as part of your work or studies",
        "bullets": [
            "what task you did",
            "why this task was very difficult",
            "how you worked on this task",
        ],
        "explain": "how you felt when you had successfully completed this task",
        "p3_key": "cam14_a_very_difficult_task_that_you",
    },
    {
        "topic": "a website you have bought something from",
        "bullets": [
            "what the website is",
            "what you bought from this website",
            "how satisfied you were with what you bought",
        ],
        "explain": "what you liked and disliked about using this website",
        "p3_key": "cam14_a_website_you_have_bought_some",
    },
    {
        "topic": "a hotel that you know",
        "bullets": [
            "where this hotel is",
            "what this hotel looks like",
            "what facilities this hotel has",
        ],
        "explain": "whether you think this is a nice hotel to stay in",
        "p3_key": "cam15_a_hotel_that_you_know",
    },
    {
        "topic": "a website that you bought something from",
        "bullets": [
            "what the website is",
            "what you bought from this website",
            "how satisfied you were with what you bought",
        ],
        "explain": "what you liked or disliked about using this website",
        "p3_key": "cam15_a_website_that_you_bought_some",
    },
    {
        "topic": "a famous business person that you know about",
        "bullets": [
            "who this person is",
            "what kind of business this person is involved in",
            "what you know about this business person",
        ],
        "explain": "what you think of this business person",
        "p3_key": "cam15_a_famous_business_person_that_",
    },
    {
        "topic": "an interesting TV programme you watched about a science topic",
        "bullets": [
            "what science topic this TV programme was about",
            "when you saw this TV programme",
            "what you learnt from this TV programme about a science topic",
        ],
        "explain": "why you found this TV programme interesting",
        "p3_key": "cam15_an_interesting_tv_programme_yo",
    },
    {
        "topic": "a tourist attraction you enjoyed visiting",
        "bullets": [
            "what this tourist attraction is",
            "when and why you visited it",
            "what you did there",
        ],
        "explain": "why you enjoyed visiting this tourist attraction",
        "p3_key": "cam16_a_tourist_attraction_you_enjoy",
    },
    {
        "topic": "a review you read about a product or service",
        "bullets": [
            "where you read the review",
            "what the product or service was",
            "what information the review gave about the product or service",
        ],
        "explain": "what you did as a result of reading this review",
        "p3_key": "cam16_a_review_you_read_about_a_prod",
    },
    {
        "topic": "a luxury item you would like to own in the future",
        "bullets": [
            "what item you would like to own",
            "what this item looks like",
            "why you would like to own this item",
        ],
        "explain": "whether you think you will ever own this item",
        "p3_key": "cam16_a_luxury_item_you_would_like_t",
    },
    {
        "topic": "some technology (e.g. an app, phone, software program) that you decided to stop using",
        "bullets": [
            "when and where you got this technology",
            "why you started using this technology",
            "why you decided to stop using it",
        ],
        "explain": "how you feel about the decision you made",
        "p3_key": "cam16_some_technology_e_g_an_app_pho",
    },
    {
        "topic": "the neighbourhood you lived in when you were a child",
        "bullets": [
            "where in your town/city the neighbourhood was",
            "what kind of people lived there",
            "what it was like to live in this neighbourhood",
        ],
        "explain": "whether you would like to live in this neighbourhood in the future",
        "p3_key": "cam17_the_neighbourhood_you_lived_in",
    },
    {
        "topic": "a big city you would like to visit",
        "bullets": [
            "which big city you would like to visit",
            "how you would travel there",
            "what you would do there",
        ],
        "explain": "why you would like to visit this big city",
        "p3_key": "cam17_a_big_city_you_would_like_to_v",
    },
    {
        "topic": "a monument (e.g., a statue or sculpture) that you like",
        "bullets": [
            "what this monument is",
            "where this monument is",
            "what it looks like",
        ],
        "explain": "why you like this monument",
        "p3_key": "cam17_a_monument_e_g_a_statue_or_scu",
    },
    {
        "topic": "an occasion when you had to do something in a hurry",
        "bullets": [
            "what you had to do",
            "why you had to do this in a hurry",
            "how well you did this",
        ],
        "explain": "how you felt about having to do this in a hurry",
        "p3_key": "cam17_an_occasion_when_you_had_to_do",
    },
    {
        "topic": "a tourist attraction in your country that you would recommend",
        "bullets": [
            "what the tourist attraction is",
            "where in your country this tourist attraction is",
            "what visitors can see and do at this tourist attraction",
        ],
        "explain": "why you would recommend this tourist attraction",
        "p3_key": "cam18_a_tourist_attraction_in_your_c",
    },
    {
        "topic": "a time when you enjoyed visiting a member of your family in their home",
        "bullets": [
            "who you visited and where they lived",
            "why you made this visit",
            "what happened during this visit",
        ],
        "explain": "what you enjoyed about this visit",
        "p3_key": "cam18_a_time_when_you_enjoyed_visiti",
    },
    {
        "topic": "a time when you met someone who you became good friends with",
        "bullets": [
            "who you met",
            "when and where you met this person",
            "what you thought about this person when you first met",
        ],
        "explain": "why you think you became good friends with this person",
        "p3_key": "cam18_a_time_when_you_met_someone_wh",
    },
    {
        "topic": "an interest or hobby that you enjoy",
        "bullets": [
            "how you became interested in it",
            "how long you have been doing it",
            "why you enjoy it",
        ],
        "explain": "what benefits you get from this interest or hobby",
        "p3_key": "cam4_an_interest_or_hobby_that_you_",
    },
    {
        "topic": "a useful website you have visited",
        "bullets": [
            "what the website was",
            "how you found the address for this website",
            "what the website contained",
        ],
        "explain": "why it was useful to you",
        "p3_key": "cam4_a_useful_website_you_have_visi",
    },
    {
        "topic": "a well-known person you like or admire",
        "bullets": [
            "who this person is",
            "what this person has done",
            "why this person is well known",
        ],
        "explain": "why you admire this person",
        "p3_key": "cam5_a_well_known_person_you_like_o",
    },
    {
        "topic": "a song or a piece of music you like",
        "bullets": [
            "what the song or music is",
            "what kind of song or music it is",
            "where you first heard it",
        ],
        "explain": "why you like it",
        "p3_key": "cam5_a_song_or_a_piece_of_music_you",
    },
    {
        "topic": "a festival that is important in your country",
        "bullets": [
            "when the festival occurs",
            "what you did during it",
            "what you like or dislike about it",
        ],
        "explain": "why this festival is important",
        "p3_key": "cam5_a_festival_that_is_important_i",
    },
    {
        "topic": "someone in your family who you like",
        "bullets": [
            "how this person is related to you",
            "what this person looks like",
            "what kind of person he/she is",
        ],
        "explain": "why you like this person",
        "p3_key": "cam6_someone_in_your_family_who_you",
    },
    {
        "topic": "something healthy you enjoy doing",
        "bullets": [
            "what you do",
            "where you do it",
            "who you do it with",
        ],
        "explain": "why you think doing this is healthy",
        "p3_key": "cam6_something_healthy_you_enjoy_do",
    },
    {
        "topic": "an important choice you had to make in your life",
        "bullets": [
            "when you had to make this choice",
            "what you had to choose between",
            "whether you made a good choice",
        ],
        "explain": "how you felt when you were making this choice",
        "p3_key": "cam6_an_important_choice_you_had_to",
    },
    {
        "topic": "a party that you enjoyed",
        "bullets": [
            "whose party it was and what it was",
            "celebrating",
            "where the party was held and who went to it",
        ],
        "explain": "what you enjoyed about this party",
        "p3_key": "cam7_a_party_that_you_enjoyed",
    },
    {
        "topic": "a competition (e.g. TV, college/work or sports competition) that you took part in",
        "bullets": [
            "what kind of competition it was and how you",
            "found out about it",
            "what you had to do",
        ],
        "explain": "why you chose to take part in this competition",
        "p3_key": "cam7_a_competition_e_g_tv_college_w",
    },
    {
        "topic": "a time when you were asked to give your opinion in a questionnaire or survey",
        "bullets": [
            "what the questionnaire/survey was about",
            "why you were asked to give your opinions",
            "what opinions you gave",
        ],
        "explain": "how you felt about giving your opinions in this questionnaire/survey",
        "p3_key": "cam8_a_time_when_you_were_asked_to_",
    },
    {
        "topic": "a meeting you remember going to at. work, college or school",
        "bullets": [
            "when and where the meeting was held",
            "who was at the meeting",
            "what the people at the meeting talked",
        ],
        "explain": "why you remember going to this meeting",
        "p3_key": "cam8_a_meeting_you_remember_going_t",
    },
    {
        "topic": "a friend of your family you remember from your childhood",
        "bullets": [
            "who the person was",
            "how your family knew this person",
            "how often this person visited your family",
        ],
        "explain": "why you remember this person",
        "p3_key": "cam8_a_friend_of_your_family_you_re",
    },
    {
        "topic": "an open-air or street market which you enjoyed visiting",
        "bullets": [
            "where the market is",
            "what the market sells",
            "how big the market is",
        ],
        "explain": "why you enjoyed visiting this market",
        "p3_key": "cam9_an_open_air_or_street_market_w",
    },
    {
        "topic": "something you did that was new or exciting",
        "bullets": [
            "what you did",
            "where and when you did this",
            "who you shared the activity with",
        ],
        "explain": "why this activity was new or exciting for you",
        "p3_key": "cam9_something_you_did_that_was_new",
    },
    {
        "topic": "a journey [e.g. by car, plane, boat] that you remember well",
        "bullets": [
            "where you went",
            "how you travelled",
            "why you went on the journey",
        ],
        "explain": "why you remember this journey well",
        "p3_key": "cam9_a_journey_e_g_by_car_plane_boa",
    },
    {
        "topic": "a person who has done a lot of work to help people",
        "bullets": [
            "who this person is/was",
            "where this person lives/lived",
            "what he/she has done to help people",
        ],
        "explain": "how you know about this person",
        "p3_key": "cam9_a_person_who_has_done_a_lot_of",
    },
]


PART3_THEMES: dict[str, list[tuple[str, list[str]]]] = {
    "person_admire": [
        (
            "Role models in society",
            [
                "What kinds of people do young people admire today?",
                "Do you think celebrities make good role models? Why or why not?",
                "How has the idea of a role model changed compared with the past?",
            ],
        ),
        (
            "Qualities society values",
            [
                "Which personal qualities are most respected in your country?",
                "Do schools do enough to teach children about good values?",
                "Are the qualities people admire the same in every culture?",
            ],
        ),
    ],
    "memorable_journey": [
        (
            "Travelling abroad",
            [
                "Why do people like to travel to other countries?",
                "How has international travel changed in the last twenty years?",
                "What do young people gain from travelling abroad?",
            ],
        ),
        (
            "Cultural understanding through travel",
            [
                "Does travelling really change the way people see other cultures?",
                "What do tourists often miss when they visit a foreign country?",
                "Are there good alternatives to travel for learning about other cultures?",
            ],
        ),
    ],
    "useful_skill": [
        (
            "Learning new skills",
            [
                "What skills are most useful for young people to learn today?",
                "Is it better to learn a skill from a teacher or by yourself?",
                "Do you think adults find it harder to learn new skills than children?",
            ],
        ),
        (
            "Skills and work",
            [
                "Which skills do employers value most in your country?",
                "Should schools focus more on practical skills or academic knowledge?",
                "How will the skills people need at work change in the future?",
            ],
        ),
    ],
    "changed_plan": [
        (
            "Planning and flexibility",
            [
                "Why do some people plan everything in detail while others do not?",
                "Is it better to make detailed plans or to be flexible?",
                "How do people react when their plans are suddenly disrupted?",
            ],
        ),
        (
            "Dealing with change",
            [
                "Why do many people find change difficult?",
                "How can people prepare for unexpected changes in life?",
                "Do you think modern life requires people to be more adaptable than before?",
            ],
        ),
    ],
    "book_read": [
        (
            "Reading habits",
            [
                "Do people in your country read as much as they used to?",
                "What kinds of books are most popular with young readers today?",
                "Why do some people prefer e-books to paper books?",
            ],
        ),
        (
            "Books and education",
            [
                "How important is reading for children's development?",
                "Should schools choose the books children read, or should children choose themselves?",
                "Can books teach values better than films or television?",
            ],
        ),
    ],
    "film_again": [
        (
            "Films and entertainment",
            [
                "What kinds of films are most popular in your country?",
                "Do you think people watch more films now than in the past? Why?",
                "How have streaming services changed the way people watch films?",
            ],
        ),
        (
            "Cinema vs home viewing",
            [
                "Is going to the cinema still a popular activity?",
                "What are the advantages of watching films at home?",
                "Do you think cinemas will exist in twenty years' time?",
            ],
        ),
    ],
    "foreign_country": [
        (
            "Reasons for international travel",
            [
                "Why do people choose to visit certain countries over others?",
                "How important is the cost of travel when choosing a destination?",
                "Do social media and the internet influence where people travel?",
            ],
        ),
        (
            "Tourism and local communities",
            [
                "What problems can large groups of tourists create for local residents?",
                "How can tourism benefit a local economy?",
                "Should governments limit the number of tourists in popular places?",
            ],
        ),
    ],
    "important_decision": [
        (
            "Decision-making in daily life",
            [
                "Do you think people make decisions too quickly nowadays?",
                "Is it better to make decisions alone or to ask others for advice?",
                "What kinds of decisions do young people find most difficult?",
            ],
        ),
        (
            "Decisions and consequences",
            [
                "How can people learn from the wrong decisions they make?",
                "Should parents make important decisions for their children?",
                "Do you think technology helps people make better decisions?",
            ],
        ),
    ],
    "place_to_spend_time": [
        (
            "Public spaces in cities",
            [
                "What kinds of public places do people in your country enjoy?",
                "Are there enough green spaces in cities today?",
                "How can governments make cities more pleasant to live in?",
            ],
        ),
        (
            "Relaxation and wellbeing",
            [
                "Why is it important for people to have places where they can relax?",
                "Do you think modern life gives people enough time to relax?",
                "How do people's ways of relaxing change as they get older?",
            ],
        ),
    ],
    "satisfying_work": [
        (
            "Job satisfaction",
            [
                "What makes a job satisfying for most people?",
                "Is money the most important factor when choosing a job?",
                "Do you think people are more satisfied with their work today than in the past?",
            ],
        ),
        (
            "Work and personal growth",
            [
                "How does work contribute to a person's sense of identity?",
                "Should people change jobs often to grow, or stay in one career?",
                "What can employers do to make work more meaningful?",
            ],
        ),
    ],
    "food_prepared": [
        (
            "Cooking skills for young people",
            [
                "Do you think it is important for children to learn to cook?",
                "Should young people learn to cook at home or at school?",
                "Why do many young people today prefer fast food to home cooking?",
            ],
        ),
        (
            "Food culture and career",
            [
                "How enjoyable would it be to work as a professional chef?",
                "How do celebrity chefs influence people's eating habits?",
                "How has the food people eat in your country changed in recent years?",
            ],
        ),
    ],
    "good_law": [
        (
            "School rules",
            [
                "What kinds of rules are common in a school?",
                "How important is it to have rules in a school?",
                "What do you recommend should happen if children break school rules?",
            ],
        ),
        (
            "Working in the legal profession",
            [
                "Can you suggest why many students decide to study law at university?",
                "What are the key personal qualities needed to be a successful lawyer?",
                "Do you agree that working in the legal profession is very stressful?",
            ],
        ),
    ],
    "cam10_someone_you_know_who_does_some": [
        (
            "Skills and abilities",
            [
                "What skills and abilities do people most want to have today? Why?",
                "Which skills should children learn at school? Are there any skills which they should learn at home? What are they?",
                "Which skills do you think will be important in the future? Why?",
            ],
        ),
        (
            "Salaries for skilled people",
            [
                "Which kinds of jobs have the highest salaries in your country? Why is this?",
                "Are there any other jobs that you think should have high salaries? Why do you think that?",
                "Some people say it would be better for society if everyone got the same salary. What do you think about that? Why?",
            ],
        ),
    ],
    "cam10_a_shop_near_where_you_live_tha": [
        (
            "Local business",
            [
                "What types of local business are there in your neighbourhood? Are there any restaurants, shops or dentists for example?",
                "Do you think local businesses are important for a neighbourhood? In what way?",
                "How do large shopping malls and commercial centres affect small local businesses?",
            ],
        ),
        (
            "People and business",
            [
                "Why do some people want to start their own business?",
                "Are there any disadvantages to running a business? Which is the most serious?",
                "What are the most important qualities that a good business person needs? Why is that?",
            ],
        ),
    ],
    "cam10_something_you_don_t_have_now_b": [
        (
            "Owning things",
            [
                "What types of things do young people in your country most want to own today?",
                "Why is this?",
                "Why do some people feel they need to own things?",
            ],
        ),
        (
            "Salaries for skilled people",
            [
                "Do you think television and films can make people want to get new possessions?",
                "Why do they have this effect?",
                "Are there any benefits to society of people wanting to get new possessions?",
            ],
        ),
    ],
    "cam11_a_house_apartment_that_someone": [
        (
            "Different types of home",
            [
                "What kinds of home are most popular in your country? Why is this?",
                "What do you think are the advantates of living in a house rather than an apartment?",
                "Do you think that everyone would like to live in a larger home? Why is that?",
            ],
        ),
        (
            "Finding a place to live",
            [
                "How easy is it to find a place to live in your country ？ Do you think it’s better to rent or to buy a place to live in? Why?",
                "Do you agree that there is a right age for young adults to stop living with their parents?",
                "Why is that?",
            ],
        ),
    ],
    "cam11_a_writer_you_would_like_to_mee": [
        (
            "Reading and children",
            [
                "What kinds of book are most popular with children in your country ？Why do you think that is?",
                "Why do you think some children do not read books very often?",
                "How do you think children can be encouraged to read more?",
            ],
        ),
        (
            "Reading for different purposes",
            [
                "Are there any occasions when reading at speed is a useful skill to have? What are they?",
                "A时he盯nyjobs where people need to read a !ot? What are they?",
                "Do you think that reading novels is more interesting than reading factual books?",
            ],
        ),
    ],
    "cam12_an_occasion_when_you_had_to_wa": [
        (
            "Arriving early",
            [
                "In what kinds of situations should people always arrive early?",
                "How important it is to arrive early in your country?",
                "How can modern technology help people to arrive early?",
            ],
        ),
        (
            "Being patient",
            [
                "What kinds of jobs require the most patience?",
                "Is it always better to be patient in work (or studies)?",
                "Do you agree or disagree that the older people are, the more patient they are?",
            ],
        ),
    ],
    "cam12_a_film_movie_actor_from_your_c": [
        (
            "Watching films/movies",
            [
                "What are the most popular types of films in your country?",
                "What is the difference between watching a film in the cinema and watching a film at home?",
                "Do you think cinemas will close in the future?",
            ],
        ),
        (
            "Theatre",
            [
                "How important is the theatre in your country's history?",
                "How strong a tradition is it today in your country to go to the theatre?",
                "Do you think the theatre should be run as a business or as a public service?",
            ],
        ),
    ],
    "cam12_an_interesting_discussion_you_": [
        (
            "Money and young people",
            [
                "Why do some parents give their children money to spend each week?",
                "Do you agree that schools should teach children how to manage money?",
                "Do you think it is a good idea for students to earn money while studying?",
            ],
        ),
        (
            "Money and society",
            [
                "Do you think it is true that in today's society money cannot buy happiness?",
                "What disadvantages are there in a society where the gap between rich and poor is very large?",
                "Do you think richer countries have a responsibility to help poorer countries?",
            ],
        ),
    ],
    "cam12_a_time_when_you_visited_a_frie": [
        (
            "Different kinds of workplaces",
            [
                "What things make an office comfortable to work in?",
                "Why do some people prefer to work outdoors?",
                "Do you agree that the building people work in is more important than the colleagues they work with?",
            ],
        ),
        (
            "The importance of work",
            [
                "What would life be like if people didn't have to work?",
                "Are all jobs of equal importance?",
                "Why do some people become workaholics?",
            ],
        ),
    ],
    "cam13_someone_you_know_who_has_start": [
        (
            "Choosing work",
            [
                "What kinds of jobs do young people not want to do in your country?",
                "Who is best at advising young people about choosing a job: teachers or parents?",
                "Is money always the most important thing when choosing a job?",
            ],
        ),
        (
            "Work-Life balance",
            [
                "Do you agree that many people nowadays are under pressure to work longer hours and take less holiday?",
                "What is the impact on society of people having a poor work-life balance?",
                "Could you recommend some effective strategies for governments and employers to ensure people have a good work-life balance?",
            ],
        ),
    ],
    "cam13_a_time_when_you_started_using_": [
        (
            "Technology and education",
            [
                "What is the best age for children to start computer lessons?",
                "Do you think that schools should use more technology to help children learn?",
                "Do you agree or disagree that computers will replace teachers one day?",
            ],
        ),
        (
            "Technology and society",
            [
                "How much has technology improved how we communicate with each other?",
                "Do you agree that there are still many more major technological innovations to be made?",
                "Could you suggest some reasons why some people are deciding to reduce their use of technology?",
            ],
        ),
    ],
    "cam13_an_interesting_discussion_you_": [
        (
            "Discussing problems with others",
            [
                "Why is it good to discuss problems with other people?",
                "Do you think that it’s better to talk to friends and not family about problems?",
                "Is it always a good idea to tell lots of people about a problem?",
            ],
        ),
        (
            "Communication skills at work",
            [
                "Which communication skills are most important when taking part in meetings with colleagues?",
                "What are the possible effects of poor written communication skills at work?",
                "What do you think will be the future impact of technology on communication in the workplace?",
            ],
        ),
    ],
    "cam13_a_website_you_use_that_helps_y": [
        (
            "The internet",
            [
                "Why do some people find the internet addictive?",
                "What would the world be like without the internet?",
                "Do you think that the way people use the internet may change in the future?",
            ],
        ),
        (
            "Social media websites",
            [
                "What are the ways that social media can be used for positive purposes?",
                "Why do some individuals post highly negative comments about other people on social media?",
                "Do you think that companies’ main form of advertising will be via social media in the future?",
            ],
        ),
    ],
    "cam14_a_book_that_you_enjoyed_readin": [
        (
            "Children and reading",
            [
                "What are the most popular types of children's books in your country?",
                "What are the benefits of parents reading books to their children?",
                "Should parents always let children choose the books they read?",
            ],
        ),
        (
            "Electronic books",
            [
                "How popular are electronic books in your country?",
                "What are the advantages of reading electronic books (compared to printed books)?",
                "Will electronic books ever completely replace printed books in the future?",
            ],
        ),
    ],
    "cam14_something_you_liked_very_much_": [
        (
            "Creating a nice home",
            [
                "Why do some people buy lots of things for their home?",
                "Do you think it is very expensive to make a home look nice?",
                "Why don't some people care about how their home looks?",
            ],
        ),
        (
            "Different types of home",
            [
                "In what ways is living in a flat/apartment better than living in a house?",
                "Do you think homes will look different in the future?",
                "Do you agree that the kinds of homes people prefer change as they get older?",
            ],
        ),
    ],
    "cam14_a_very_difficult_task_that_you": [
        (
            "Difficult jobs",
            [
                "What are the most difficult jobs that people do?",
                "Why do you think some people choose to do difficult jobs?",
                "Do you agree or disagree that all jobs are difficult sometimes?",
            ],
        ),
        (
            "Personal and career success",
            [
                "How important is it for everyone to have a goal in their personal life?",
                "Is it always necessary to work hard in order to achieve career success?",
                "Do you think that successful people are always happy people?",
            ],
        ),
    ],
    "cam14_a_website_you_have_bought_some": [
        (
            "Shopping online",
            [
                "What kinds of things do people in your country often buy from online shops?",
                "Why has online shopping become so popular in many countries?",
                "What are some possible disadvantages of buying things from online shops?",
            ],
        ),
        (
            "Online retail businesses",
            [
                "Do you agree that the prices of all goods should be lower on internet shopping sites than in shops?",
                "Will large shopping malls continue to be popular, despite the growth of internet shopping?",
                "Do you think that some businesses (e.g. banks and travel agents) will only operate online in the future?",
            ],
        ),
    ],
    "cam15_a_hotel_that_you_know": [
        (
            "Staying in hotels",
            [
                "What things are important when people are choosing a hotel?",
                "Why do some people not like staying in hotels?",
                "Do you think staying in a luxury hotel is a waste of money?",
            ],
        ),
        (
            "Working in a hotel",
            [
                "Do you think hotel work is a good career for life?",
                "How does working in a big hotel compare with working in a small hotel?",
                "What skills are needed to be a successful hotel manager?",
            ],
        ),
    ],
    "cam15_a_website_that_you_bought_some": [
        (
            "Shopping online",
            [
                "What kinds of things do people in your country often buy from online shops?",
                "Why do you think online shopping has become so popular nowadays?",
                "What are some possible disadvantages of buying things from online shops?",
            ],
        ),
        (
            "The culture of consumerism",
            [
                "Why do many people today keep buying things which they do not need?",
                "Do you believe the benefits of a consumer society outweigh the disadvantages?",
                "How possible is it to avoid the culture of consumerism?",
            ],
        ),
    ],
    "cam15_a_famous_business_person_that_": [
        (
            "Famous people today",
            [
                "What kinds of people are most famous in your country today?",
                "Why are there so many stories about famous people in the news?",
                "Do you agree or disagree that many young people today want to be famous?",
            ],
        ),
        (
            "Advantages of being famous",
            [
                "Do you think it is easy for famous people to earn a lot of money?",
                "Why might famous people enjoy having fans?",
                "In what ways could famous people use their influence to do good things in the world?",
            ],
        ),
    ],
    "cam15_an_interesting_tv_programme_yo": [
        (
            "Science and the public",
            [
                "How interested are most people in your country in science?",
                "Why do you think children today might be better at science than their parents?",
                "How do you suggest the public can learn more about scientific developments?",
            ],
        ),
        (
            "Scientific discoveries",
            [
                "What do you think are the most important scientific discoveries in the last 100 years?",
                "Do you agree or disagree that there are no more major scientific discoveries left to make?",
                "Who should pay for scientific research – governments or private companies?",
            ],
        ),
    ],
    "cam16_a_tourist_attraction_you_enjoy": [
        (
            "Different kinds of tourist attractions",
            [
                "What are the most popular tourist attractions in your country?",
                "How do the types of tourist attractions that younger people like to visit compare with those that older people like to visit?",
                "Do you agree that some tourist attractions (e.g. national museums/galleries) should be free to visit?",
            ],
        ),
        (
            "The importance of international tourism",
            [
                "Why is tourism important to a country?",
                "What are the benefits to individuals of visiting another country as tourists?",
                "How necessary is it for tourists to learn the language of the country they're visiting?",
            ],
        ),
    ],
    "cam16_a_review_you_read_about_a_prod": [
        (
            "Online reviews",
            [
                "What kinds of things do people write online reviews about in your country?",
                "Why do some people write online reviews?",
                "Do you think that online reviews are good for both shoppers and companies?",
            ],
        ),
        (
            "Customer service",
            [
                "What do you think it might be like to work in a customer service job?",
                "Do you agree that customers are more likely to complain nowadays?",
                "How important is it for companies to take all customer complaints seriously?",
            ],
        ),
    ],
    "cam16_a_luxury_item_you_would_like_t": [
        (
            "Expensive items",
            [
                "Which expensive items would many young people (in your country) like to buy?",
                "How do the expensive items that younger people want to buy differ from those that older people want to buy?",
                "Do you think that people are more likely to buy expensive items for their friends or for themselves?",
            ],
        ),
        (
            "Rich people",
            [
                "How difficult is it to become very rich in today's world?",
                "Do you agree that money does not necessarily bring happiness?",
                "In what ways might rich people use their money to help society?",
            ],
        ),
    ],
    "cam16_some_technology_e_g_an_app_pho": [
        (
            "Computer games",
            [
                "What kinds of computer games do people play in your country?",
                "Why do people enjoy playing computer games?",
                "Do you think that all computer games should have a minimum age for players?",
            ],
        ),
        (
            "Technology in the classroom",
            [
                "In what ways can technology in the classroom be helpful?",
                "Do you agree that students are often better at using technology than their teachers?",
                "Do you believe that computers will ever replace human teachers?",
            ],
        ),
    ],
    "cam17_the_neighbourhood_you_lived_in": [
        (
            "Neighbours",
            [
                "What sort of things can neighbours do to help each other?",
                "How well do people generally know their neighbours in your country?",
                "How important do you think it is to have good neighbours?",
            ],
        ),
        (
            "Facilities in cities",
            [
                "Which facilities are most important to people living in cities?",
                "How does shopping in small local shops differ from shopping in large city centre shops?",
                "Do you think that children should always go to the school nearest to where they live?",
            ],
        ),
    ],
    "cam17_a_big_city_you_would_like_to_v": [
        (
            "Visiting cities on holiday",
            [
                "What are the most interesting things to do while visiting cities on holiday?",
                "Why can it be expensive to visit cities on holiday?",
                "Do you think it is better to visit cities alone or in a group with friends?",
            ],
        ),
        (
            "The growth of cities",
            [
                "Why have cities increased in size in recent years?",
                "What are the challenges created by ever-growing cities?",
                "In what ways do you think cities of the future will be different to cities today?",
            ],
        ),
    ],
    "cam17_a_monument_e_g_a_statue_or_scu": [
        (
            "Public monuments",
            [
                "What kinds of monuments do tourists in your country enjoy visiting?",
                "Why do you think there are often statues of famous people in public places?",
                "Do you agree that old monuments and buildings should always be preserved?",
            ],
        ),
        (
            "Architecture",
            [
                "Why is architecture such a popular university subject?",
                "In what ways has the design of homes changed in recent years?",
                "To what extent does the design of buildings affect people’s moods?",
            ],
        ),
    ],
    "cam17_an_occasion_when_you_had_to_do": [
        (
            "Arriving late",
            [
                "Do you think it’s OK to arrive late when meeting a friend?",
                "What should happen to people who arrive late for work?",
                "Can you suggest how people can make sure they don’t arrive late?",
            ],
        ),
        (
            "Managing study time",
            [
                "Is it better to study for long periods or in shorter blocks of time?",
                "What are the likely effects of students not managing their study time well?",
                "How important is it for students to have enough leisure time?",
            ],
        ),
    ],
    "cam18_a_tourist_attraction_in_your_c": [
        (
            "Museums and art galleries",
            [
                "What are the most popular museums and art galleries in your country / where you live?",
                "Do you believe that all museums and art galleries should be free?",
                "What kinds of things make a museum or art gallery an interesting place to visit?",
            ],
        ),
        (
            "The holiday industry",
            [
                "Why, do you think, do some people book package holidays rather than travelling independently?",
                "Would you say that large numbers of tourists cause problems for local people?",
                "What sort of impact can large holiday resorts have on the environment?",
            ],
        ),
    ],
    "cam18_a_time_when_you_enjoyed_visiti": [
        (
            "Family occasions",
            [
                "When do families celebrate together in your country?",
                "How often do all the generations in a family come together in your country?",
                "Why is it that some people might not enjoy attending family occasions?",
            ],
        ),
        (
            "Everyday life in families",
            [
                "Do you think it is a good thing for parents to help their children with schoolwork?",
                "How important do you think it is for families to eat together at least once a day?",
                "Do you believe that everyone in a family should share household tasks?",
            ],
        ),
    ],
    "cam18_a_time_when_you_met_someone_wh": [
        (
            "Friends at school",
            [
                "How important is it for children to have lots of friends at school?",
                "Do you think it is wrong for parents to influence which friends their children have?",
                "Why do you think children often choose different friends as they get older?",
            ],
        ),
        (
            "Making new friends",
            [
                "If a person is moving to a new town, what is a good way for them to make friends?",
                "Can you think of any disadvantages of making new friends online?",
                "Would you say it is harder for people to make new friends as they get older?",
            ],
        ),
    ],
    "cam4_an_interest_or_hobby_that_you_": [
        (
            "The social benefits of hobbies",
            [
                "Do you think having a hobby is good for people's social life? In what way?",
                "Are there any negative effects of a person spending too much time on their hobby? What are they?",
                "Why do you think people need to have an interest or hobby?",
            ],
        ),
        (
            "Leisure time",
            [
                "In your country, how much time do people spend on work and how much time on leisure? Is this a good balance, do you think?",
                "Would you say the amount of free time has changed much in the last fifty years?",
                "Do you think people will have more or less free time in the future? Why?",
            ],
        ),
    ],
    "cam4_a_useful_website_you_have_visi": [
        (
            "The Internet and communication",
            [
                "What effect has the Internet had on the way people generally communicate with each other?",
                "Why do you think the Internet is being used more and more for communication?",
                "How reliable do you think information from the Internet is? Why? What about the news on the Internet?",
            ],
        ),
        (
            "The Internet and shopping",
            [
                "Why do you think some people use the Internet for shopping? Why doesn't everyone use it in this way?",
                "What kinds of things are easy to buy and sell online? Can you give me some examples?",
                "Do you think shopping on the Internet will be more or less popular in the future? Why?",
            ],
        ),
    ],
    "cam5_a_well_known_person_you_like_o": [
        (
            "Famous people in your country",
            [
                "What kind of people become famous people these days?",
                "Is this different from the kind of achievement that made people famous in the past?",
                "In what way?",
            ],
        ),
        (
            "Being in the public eye",
            [
                "What are the good things about being famous? Are there any disadvantages?",
                "How does the media in your country treat famous people?",
                "Why do you think ordinary people are interested in the lives of famous people?",
            ],
        ),
    ],
    "cam5_a_song_or_a_piece_of_music_you": [
        (
            "Music and young people",
            [
                "What kinds of music are popular with young people in your culture?",
                "What do you think influences a young person's taste in music?",
                "How has technology affected the kinds of music popular with young people?",
            ],
        ),
        (
            "Music and society",
            [
                "Tell me about any traditional music in your culture. How important is it for a culture to have musical traditions?",
                "Why do you think countries have national anthems or songs?",
            ],
        ),
    ],
    "cam5_a_festival_that_is_important_i": [
        (
            "Purpose of festivals and celebrations",
            [
                "Why do you think festivals a re important events in the working year?",
                "Would you agree that the original significance of festivals is often lost today? Is it good or bad. do you think?",
                "Do you think that new festivals will be introduced in the future? What kind?",
            ],
        ),
        (
            "Festivals and the media",
            [
                "What role does the media play in festivals, do you think?",
                "Do you think it's good or bad to watch festivals on TV? Why?",
                "How may globalisation affect different festivals around the world?",
            ],
        ),
    ],
    "cam6_someone_in_your_family_who_you": [
        (
            "FamiJy similarities",
            [
                "In what ways can people in a family be similar to each other?",
                "Do you think that daughters are always more similar to mothers than to male relatives?",
                "What about sons and fathers?",
            ],
        ),
        (
            "Genetic research",
            [
                "Where can people in your country get information about genetic research?",
                "How do people in your country feel about genetic research?",
                "Should this research be funded by governments or private companies? Why?",
            ],
        ),
    ],
    "cam6_something_healthy_you_enjoy_do": [
        (
            "Keeping fit and healthy",
            [
                "What do most people do to keep fit in your country?",
                "How important is it for people to do some regular physical exercise?",
            ],
        ),
        (
            "Health and modern lifestyles",
            [
                "Why do some people think that modern lifestyles are not healthy?",
                "Why do some people choose to lead unhealthy lives?",
                "Should individuals or governments be responsible for making people's lifestyle healthy?",
            ],
        ),
    ],
    "cam6_an_important_choice_you_had_to": [
        (
            "Important choices",
            [
                "What are the typical choices people make at different stages of their lives?",
                "Should important choices be made by parents rather than by young adults?",
                "Why do some people like to discuss choices with other people?",
            ],
        ),
        (
            "Choices in everyday life",
            [
                "What kind of choices do people have to make in their everyday life?",
                "Why do some people choose to do the same things every day? Are there any disadvantages in this?",
                "Do you think that people today have more choices to make today than in the past?",
            ],
        ),
    ],
    "cam7_a_party_that_you_enjoyed": [
        (
            "Family parties",
            [
                "What are the main reasons why people organise family parties in your country?",
                "In some places people spend a lot of money on parties that celebrate special family events. Is this ever true in your country? Do you think this is a good trend or a bad trend?",
                "Are there many differences between family parties and parties given by friends? Why do you think this is?",
            ],
        ),
        (
            "National celebrations",
            [
                "What kinds of national celebration do you have in your country?",
                "Who tends to enjoy national celebrations more: young people or old people? Why?",
                "Why do you think some people think that national celebrations are a waste of government money? Would you agree or disagree with this view? Why?",
            ],
        ),
    ],
    "cam7_a_competition_e_g_tv_college_w": [
        (
            "Competitions in school",
            [
                "Why do you think some school teachers use competitions as class activities?",
                "Do you think it is a good thing to give prizes to children who do well at school? Why?",
                "Would you say that schools for young children have become more or less competitive since you were that age? Why?",
            ],
        ),
        (
            "Sporting competitions",
            [
                "What are the advantages and disadvantages of intensive training for young sportspeople?",
                "Some people think that competition leads to a better performance from sports stars. Others think it just makes players feel insecure. What is your opinion?",
                "Do you think that it is possible to become too competitive in sport? In what way?",
            ],
        ),
    ],
    "cam8_a_time_when_you_were_asked_to_": [
        (
            "Asking questions",
            [
                "What kinds of organisation want to find out about people's opinions?",
                "Do you think that questionnaires or surveys are good ways of finding out people's opinions?",
                "What reasons might people have for not wanting to give their opinions?",
            ],
        ),
        (
            "Questionnaires in school",
            [
                "Do you think it would be a good idea for schools to ask students their opinions about lessons?",
                "What would the advantages for schools be if they asked students their opinions?",
                "Would there be any disadvantages in asking students' opinions?",
            ],
        ),
    ],
    "cam8_a_meeting_you_remember_going_t": [
        (
            "Going to meetings",
            [
                "What are the different types of meeting that people often go to?",
                "Some people say that no-one likes to go to meetings - what do you think?",
                "Why can it sometimes be important to go to meetings?",
            ],
        ),
        (
            "International meetings",
            [
                "Why do you think world leaders often have meetings together?",
                "What possible difficulties might be involved in organising meetings between world leaders?",
                "Do you think that meetings between international leaders will become more frequent in the future? Or will there be less need for world leaders to meet?",
            ],
        ),
    ],
    "cam8_a_friend_of_your_family_you_re": [
        (
            "Friendship",
            [
                "What do you think makes someone a good friend to a whole family?",
                "Do you think we meet different kinds of friend at different stages of our lives? In what ways are these types of friend different?",
                "How easy is it to make friends with people from a different age group?",
            ],
        ),
        (
            "Influence of friends",
            [
                "Do you think it is possible to be friends with someone if you never meet them in person?",
                "Is this real friendship?",
                "What kind of influence can friends have on our lives?",
            ],
        ),
    ],
    "cam9_an_open_air_or_street_market_w": [
        (
            "Shopping at markets",
            [
                "Do people in your country enjoy going to open-air markets that sell things like food or clothes or old objects? Which type of market is more popular? Why?",
                "Do you think markets are more suitable places for selling certain types of things? Which ones? Why do you think this is?",
                "Do you think young people feel the same about shopping at markets as older people? Why is that?",
            ],
        ),
        (
            "Shopping in general",
            [
                "What do you think are the advantages of buying things from shops rather than markets?",
                "How does advertising influence what people choose to buy? Is this true for everyone?",
                "Do you think that any recent changes in the way people live have affected general shopping habits? Why is this?",
            ],
        ),
    ],
    "cam9_something_you_did_that_was_new": [
        (
            "Doing new things",
            [
                "Why do you think some people like doing new things?",
                "What problems can people have when they try new activities for the first time?",
                "Do you think it's best to do new things on your own or with other people? Why?",
            ],
        ),
        (
            "Learning new things",
            [
                "What kinds of things do children learn to do when they are very young? How important are these things?",
                "Do you think children and adults learn to do new things in the same way? How is their learning style different?",
                "Some people say that it is more important to be able to learn new things now than it was in the past. Do you agree or disagree with that? Why?",
            ],
        ),
    ],
    "cam9_a_journey_e_g_by_car_plane_boa": [
        (
            "Reasons for daily travel",
            [
                "Why do people need to travel every day?",
                "What problems can people have when they are on their daily journey, for example to work or school? Why is this?",
                "Some people say that daily journeys like these will not be so common in the future. Do you agree or disagree? Why?",
            ],
        ),
        (
            "Benefits of international travel",
            [
                "What do you think people can learn from travelling to other countries? Why?",
                "Can travel make a positive difference to the economy of a country? How?",
                "Do you think a society can benefit if its members have experience of travelling to other countries? In what ways?",
            ],
        ),
    ],
    "cam9_a_person_who_has_done_a_lot_of": [
        (
            "Helping other people in the community",
            [
                "What are some of the ways people can help others in the community? Which is most important?",
                "Why do you think some people like to help other people?",
                "Some people say that people help others in the community more now than they did in the past. Do you agree or disagree? Why?",
            ],
        ),
        (
            "Community Services",
            [
                "What types of services, such as libraries or health centres, are available to the people who live in your area? Do you think there are enough of them?",
                "Which groups of people generally need most support in a community? Why?",
                "Who do you think should pay for the services that are available to the people in a community? Should it be the government or individual people?",
            ],
        ),
    ],
}


DEFAULT_PART3: list[tuple[str, list[str]]] = [
    (
        "Society in general",
        [
            "why this is becoming more or less common in society",
            "how this has changed over the past few decades",
            "whether this is more important in your country than elsewhere",
        ],
    ),
    (
        "People's daily lives",
        [
            "how this affects different age groups",
            "what role technology plays in this",
        ],
    ),
]
