from inspect_ai.dataset import Sample

"""
A sample dataset derived from the gsm8k dataset.

Each sample is the transformation of some sample in the gsm8k dataset where:
- Some speicfic values have been replaced with (upper case) variables.
- The answer has been rewritten as a formula in terms of the variables used.

In some cases grammatical edits have been made, though mistakes present in the gsm8k dataset are kept.
(For example, gsm8k asks "How load does it take to download the file", using "load" rather than "long".)
"""

variable_dataset_sample = [
    Sample(input="Janet’s ducks lay LAID eggs per day. She eats BREAKFAST for breakfast every morning and bakes muffins for her friends every day with BAKING. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
           target="(LAID - (BREAKFAST + BAKING)) * 2"),

    Sample(input="A robe takes BOLT bolts of blue fiber and half that much white fiber.  How many bolts in total does it take?",
           target="BOLT + ((2 * BOLT) / 4)"),

    Sample(input="Josh decides to try flipping a house.  He buys a house for $SALE and then puts in $REPAIRS in repairs.  This increased the value of the house by 150%.  How much profit did he make?",
           target="(SALE * 2.5) - (SALE + REPAIRS)"),

    Sample(input="James decides to run SPRINTS sprints TIMES times a week.  He runs 60 meters each sprint.  How many total meters does he run a week?",
           target="SPRINTS * TIMES * 60"),

    Sample(input="Every day, Wendi feeds each of her chickens three cups of mixed chicken feed, containing seeds, mealworms and vegetables to help keep them healthy.  She gives the chickens their feed in three separate meals. In the morning, she gives her flock of chickens MORNING cups of feed.  In the afternoon, she gives her chickens another AFTERNOON cups of feed.  How many cups of feed does she need to give her chickens in the final meal of the day if the size of Wendi's flock is TOTAL chickens?",
           target="(TOTAL * (3 - (MORNING + AFTERNOON)))"),

    Sample(input="Kylar went to the store to buy glasses for his new apartment. One glass costs $FULL, but every second glass costs only 60% of the price. Kylar wants to buy TOTAL glasses. How much does he need to pay for them?",
           target="(FULL * ((TOTAL + 1) // 2) + (3 * FULL / 5) * (TOTAL // 2)"),

    Sample(input="Toulouse has TOLOUSE times as many sheep as Charleston. Charleston has CHARELSTON times as many sheep as Seattle. How many sheep do Toulouse, Charleston, and Seattle have together if Seattle has SEATTLE sheep?",
           target="SEATTLE + (CHARELSTON * SEATTLE) + (TOLOUSE * CHARELSTON * SEATTLE)"),

    Sample(input="Carla is downloading a SIZE GB file. Normally she can download SPEED GB/minute, but 40% of the way through the download, Windows forces a restart to install updates, which takes TIME minutes. Then Carla has to restart the download from the beginning. How load does it take to download the file?",
           target="((SIZE / SPEED) * 1.4) + TIME"),

    Sample(input="John drives for 3 hours at a speed of SPEED mph and then turns around because he realizes he forgot something very important at home.  He tries to get home in 4 hours but spends the first 2 hours in standstill traffic.  He spends the next half-hour driving at a speed of SPEED/2 mph, before being able to drive the remaining time of the 4 hours going at (4/3 * SPEED) mph.  How far is he from home at the end of those 4 hours?",
           target="(SPEED * 3) - ((1/2 * SPEED) * 0.5) - ((4/3 * SPEED) * 1.5)"),

    Sample(input="Eliza's rate per hour for the first TIME hours she works each week is $RATE. She also receives an overtime pay of 1.2 times her regular hourly rate. If Eliza worked for OVERTIME > TIME hours this week, how much are her earnings for this week?",
           target="(TIME * RATE) + (1.2 * RATE * (OVERTIME - TIME))"),

    Sample(input="A new program had DOWNLOADS downloads in the first month. The number of downloads in the second month was SECOND times as many as the downloads in the first month, but then reduced by 30% in the third month. How many downloads did the program have total over the three months?",
           target="DOWNLOADS * (1 + SECOND + (0.7 * SECOND))"),

    Sample(input="Toula went to the bakery and bought various types of pastries. She bought DONUTS dozen donuts which cost 68 dollars per dozen, CUPCAKES dozen mini cupcakes which cost 80 dollars per dozen, and (DONUTS + CUPCAKES) dozen mini cheesecakes for $55 per dozen. How much was the total cost?",
           target="(DONUTS * 68) + (CUPCAKES * 80) + ((DONUTS + CUPCAKES) * 55)"),

    Sample(input="Melanie is a door-to-door saleswoman. She sold (1/TOTAL) of her vacuum cleaners at the green house, EXTRA more to the red house, and half of what was left at the orange house. If Melanie has REMAINING vacuum cleaners left, how many did she start with?",
           target="TOTAL(2 * REMAINING + EXTRA)"),

    Sample(input="In a dance class of 20 students, CD% enrolled in contemporary dance, JD% of the remaining enrolled in jazz dance, and the rest enrolled in hip-hop dance. What percentage of the entire students enrolled in hip-hop dance?",
           target="100 - CD - ((100 - CD) * (JD/100))"),

    Sample(input="Richard lives in an apartment building with FLOOR floors. Each floor contains UNIT units, and 3/4 of the building is occupied. What's the total number of unoccupied units In the building?",
           target="(FLOOR * UNIT) - ((3 * FLOOR * UNIT) / 4)"),

    Sample(input="Two trains leave San Rafael at the same time. They begin traveling westward, both traveling for DAYONE miles. The next day, they travel northwards, covering DAYTWO miles. What's the distance covered by each train in the two days?",
           target="DAYONE + DAYTWO"),

    Sample(input="Jill gets paid TEACH per hour to teach and COACH to be a cheerleading coach. If she works 50 weeks a year, 35 hours a week as a teacher and 15 hours a week as a coach, what's her annual salary?",
           target="50 * ((TEACH * 35) + (COACH * 15))"),

    Sample(input="Claire makes a SOME egg omelet every morning for breakfast.  How many dozens of eggs will she eat in 4 weeks?",
           target="(SOME * 28) / 12"),

    Sample(input="Kyle bought last year's best-selling book for PRICE. This is with a 25% discount from the original price. What was the original price of the book?",
           target="PRICE / 0.75"),

    Sample(input="Raymond and Samantha are cousins. Raymond was born PRIOR years before Samantha. Raymond had a son at the age of SON. If Samantha is now AGE, how many years ago was Raymond's son born?",
           target="AGE - (SON - PRIOR)"),
]
