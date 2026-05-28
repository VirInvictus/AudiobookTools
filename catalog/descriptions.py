"""Per-book descriptions plus author/narrator constants reused across catalog entries.

Each ``DESC[key]`` is the audiobook's publisher synopsis, rewritten lightly for
voice and length. The constants below are pulled out only because they appear in
many entries; everything else lives directly in ``catalog/books.py``.
"""

from __future__ import annotations

ABERCROMBIE = "Joe Abercrombie"
PACEY = "Steven Pacey"

LINCOLN_CAST = "Nick Offerman, David Sedaris, George Saunders, Carrie Brownstein, Miranda July, Lena Dunham & a full cast"

DESC: dict[str, str] = {
    "bc1": (
        "Some say the world has ended. The Black Company, last of the Free "
        "Companies of Khatovar, is hired north to fight for the Lady, a dark "
        "mistress whose Ten Who Were Taken haunt every battlefield. Darkness wars "
        "with darkness, and the hard-bitten men of the Company take their pay and "
        "do what they must."
    ),
    "best_served_cold": (
        "War may be hell, but for Monza Murcatto, the Snake of Talins and the "
        "most feared mercenary in Duke Orso's employ, it is a good way to make a "
        "living, until her victories make her too popular for her employer's "
        "taste. Betrayed and left for dead, Monza is left with a broken body and "
        "a burning hunger for vengeance. Whatever the cost, seven men must die. "
        "Her crew includes Styria's least reliable drunkard, its most treacherous "
        "poisoner, a mass murderer obsessed with numbers, and a Northman who only "
        "wants to do the right thing."
    ),
    "bobi1": (
        "Bob Johansson, a software engineer who signed up for cryonic "
        "preservation, wakes a century later to find his mind running as software "
        "inside a powerful computer, drafted to pilot a self-replicating "
        "interstellar probe. Sent to scout out habitable worlds for a troubled "
        "Earth, Bob soon discovers his probe can build more probes; the resulting "
        "Bobs inherit his memories but quickly drift into their own "
        "personalities."
    ),
    "bourdain_kc": (
        "When Anthony Bourdain wrote Don't Eat Before You Read This in The New "
        "Yorker, he revealed what really goes on behind the kitchen door. Kitchen "
        "Confidential expanded that appetizer into a deliciously funny, "
        "delectably shocking banquet of twenty-five years of sex, drugs, and "
        "haute cuisine. From the Rainbow Room atop Rockefeller Center to the "
        "dives of the East Village, from the mobsters to the rats, Bourdain's "
        "wild-but-true tales make the belly ache with laughter."
    ),
    "caine1": (
        "Hari Michaelson, born of a disgraced family, has made himself into "
        "Caine: killer, superstar, hero. On a fantasy world called Overworld, "
        "watched by billions back on Earth as live-streamed entertainment, Caine "
        "is the studio's most lethal asset. When his estranged wife is kidnapped "
        "by an emperor with a god complex, he is sent in to save her, and the "
        "rules of the game start to break."
    ),
    "dcc4": (
        "Surviving in a multilevel dungeon that doubles as the galaxy's most "
        "watched game show has taught Coast Guard vet Carl and his "
        "ex-girlfriend's cat, Princess Donut, that the one thing they can count "
        "on, apart from each other, is never knowing what comes next. A floating "
        "fortress of warrior gnomes. A castle made of sand. A derelict submarine "
        "guarded by malfunctioning machines. A haunted crypt ringed with lethal "
        "traps. One bubble, four castles, fifteen days: capture each one and the "
        "stairwell unlocks. But Carl and his team can't do it alone, and the "
        "low-level crawlers trapped in the bubble with them may not be worth "
        "trusting."
    ),
    "dcc5": (
        "Carl and Princess Donut refuse to be prey. On the sixth floor, the "
        "Hunting Grounds, outside tourists are finally allowed into the game, and "
        "they have come to hunt. Among them is Vrah, a famed veteran stalker "
        "intent on collecting the greatest trophy of her career. Through a lush "
        "jungle teeming with savage dinosaurs and a fallen princess bent on "
        "vengeance, the crawlers must survive long enough to reach a mysterious "
        "end-of-floor celebration for the top players: the Butcher's Masquerade."
    ),
    "dcc6": (
        "A pantheon of forgotten gods. An old grudge between a talk show host, an "
        "heiress, and the man they shattered. A rapidly deteriorating AI. An "
        "inconvenient tiara on the head of a friend. As management reels from the "
        "abrupt end of the seventh level, the surviving crawlers stumble onto the "
        "eighth and find themselves scattered across a map of Earth's final days, "
        "where intangible ghosts of humanity go about their lives oblivious to "
        "the doom bearing down on them, and monsters out of Earth's lore live "
        "among them. Each team is given a task: capture six of these beasts and "
        "turn them into summonable cards. The most powerful monster in their area "
        "is Shi Maria, once married to a now-missing god, whose special attack is "
        "said to drive its victims insane. They call her the Bedlam Bride."
    ),
    "dcc8": (
        "It's off to the races in the explosive eighth book in the series. As "
        "chaos and mass panic spread outside the dungeon in the wake of the "
        "Faction Wars, Carl and Donut reach the tenth floor, where they are "
        "forced to compete in a brutal circuit of races: get from point A to "
        "point B, never come in last, and upgrade the vehicle after each "
        "increasingly lethal track. Meanwhile, nobody, not even the showrunners, "
        "knows what waits on the mysterious eleventh floor, something the system "
        "AI has ominously dubbed a coming-out party for the ages. Stripped of his "
        "agency by the rules of this floor, Carl begins planning a party of his "
        "own, a scheme so dangerous he can't risk telling his friends lest the AI "
        "put a stop to it."
    ),
    "dt1": (
        "In a world that has moved on, Roland Deschain, the last gunslinger, "
        "follows the trail of the Man in Black across an unforgiving desert in "
        "pursuit of the Dark Tower. So begins a quest that will define an entire "
        "saga."
    ),
    "dt2": (
        "Roland steps through three doors on a forsaken beach, drawing into his "
        "ka-tet the heroin-addicted Eddie Dean, the legless and divided Odetta "
        "Holmes, and a third figure of terrible importance. The gunslinger's "
        "quest gains a fellowship, and a long road begins."
    ),
    "dt3": (
        "Roland and his companions cross a poisoned, monster-haunted landscape "
        "toward the city of Lud, dodging riddles and a lunatic monorail named "
        "Blaine. The Waste Lands deepens the stakes of the journey and the cost "
        "of remembering what has been lost."
    ),
    "dt4": (
        "Trapped on Blaine the Mono, the ka-tet plays for their lives, then "
        "spills into a strange version of mid-world Kansas. Roland tells the long "
        "story of his first true love, a young woman named Susan Delgado, and of "
        "the witches, gunmen, and dark magics that shaped him."
    ),
    "exp_calibans_war": (
        "A child is missing on Ganymede, a Martian marine has watched her "
        "comrades die at the hands of something that should not exist, and a "
        "vicious Earth politician is willing to burn it all down to keep her "
        "seat. The crew of the Rocinante is pulled deeper into a war whose terms "
        "even its makers do not understand."
    ),
    "exp_leviathan_wakes": (
        "When the salvage of a drifting freighter goes bad, ice hauler Jim Holden "
        "and his small crew become reluctant witnesses to the secret that will "
        "set the inner planets and the Belt on a path to war. A detective in a "
        "corrupt station hunts for a missing woman; an alien organism waits in "
        "the dark. The first novel of the Expanse is space opera done with the "
        "bones of a noir."
    ),
    "fall_hyperion": (
        "The pilgrims have reached the Time Tombs. As the Shrike walks among "
        "them, the Hegemony's last war erupts across the worldweb and the dreams "
        "of John Keats become the channel through which a cosmic story resolves. "
        "Simmons concludes the first cycle of the Hyperion Cantos with "
        "revelation, sacrifice, and a love letter to poetry."
    ),
    "gentlemen_1": (
        "An orphan's life is harsh in the mysterious island city of Camorr, but "
        "young Locke Lamora becomes a thief under the tutelage of a gifted con "
        "artist. As leader of the band known as the Gentleman Bastards, Locke is "
        "soon infamous, fooling even the underworld's most feared ruler in a "
        "glittering, savage caper of friendship and revenge."
    ),
    "gentlemen_2": (
        "After a brutal battle with the underworld of Camorr, Locke and his "
        "sidekick Jean flee to the exotic shores of Tal Verrar to nurse their "
        "wounds. They are soon back at what they do best, stealing from the rich, "
        "with their sights set on the Sinspire, the world's most exclusive and "
        "most heavily guarded gambling house, where cheating means death."
    ),
    "hyperion": (
        "On the eve of an interstellar war, seven pilgrims journey across the "
        "planet Hyperion to seek a final audience with the Shrike, a being of "
        "legend, blood, and time. As they travel, each tells their story, and "
        "through their tales the strange ecology of the Hegemony of Man, the Time "
        "Tombs, and the deep history of the human web begins to unfold. Simmons's "
        "masterwork is a Canterbury Tales for a far-future humanity."
    ),
    "just_kids": (
        "It was the summer Coltrane died, the summer of love and riots, and the "
        "summer a chance encounter in Brooklyn brought two young people together "
        "on a path of art, devotion, and initiation. Patti Smith would become a "
        "poet and performer; Robert Mapplethorpe would direct his provocative "
        "style toward photography. Bound in innocence and ambition, they made a "
        "pact to take care of each other through the hungry years, from Coney "
        "Island to the round table of Max's Kansas City and on to the Hotel "
        "Chelsea, in a time when poetry, rock and roll, art, and sexual politics "
        "were colliding and exploding. Just Kids is Patti Smith's tribute to "
        "Robert Mapplethorpe, and a love letter to New York."
    ),
    "lolita": (
        "When it was published in 1955, Lolita immediately became a cause célèbre "
        "because of the freedom and sophistication with which it handled the "
        "unusual erotic predilections of its protagonist. But Vladimir Nabokov's "
        "wise, ironic, elegant masterpiece owes its stature as one of the "
        "twentieth century's novels of record not to the controversy its material "
        "aroused but to its author's use of that material to tell a love story "
        "almost shocking in its beauty and tenderness."
    ),
    "master_margarita": (
        "In Soviet Moscow, the Devil arrives in person with his eccentric "
        "retinue, throwing the city into a satirical frenzy of theatre, theft, "
        "and supernatural mischief. Interleaved is the parallel story of Pontius "
        "Pilate and the prisoner Yeshua Ha-Notsri, a meditation on power, mercy, "
        "and art unfinished by a Master and his devoted Margarita. Bulgakov's "
        "masterpiece, written in secret under Stalin, is a comic, terrifying, and "
        "exhilarating novel of love and faith."
    ),
    "red_country": (
        "They burned her home, they stole her brother and sister, but vengeance "
        "is following. Shy South hoped to bury her bloody past and ride away "
        "smiling, but she will have to sharpen up some bad old ways to get her "
        "family back, and she is not a woman to flinch from what needs doing. So "
        "when she and her cowardly old fellow Lamb find their farm in ruins and "
        "the children gone, they set off in pursuit across the lawless plains, "
        "through feud, duel, and massacre, high into the unmapped mountains to a "
        "final reckoning. It turns out Lamb has a bloody past of his own, and out "
        "in the badlands the past never stays buried."
    ),
    "red_rising": (
        "Darrow is a Red, a member of the lowest caste in the color-coded "
        "society of the future. He toils deep beneath the surface of Mars, "
        "believing he is making the planet livable for future generations. Then "
        "he discovers that humanity reached the surface long ago, and that he "
        "and his people are nothing but slaves to a decadent ruling class. "
        "Driven by the memory of a lost love and a longing for justice, Darrow "
        "sacrifices everything to infiltrate the legendary Institute, the "
        "proving ground of the ruling Golds, where he must compete for his "
        "life, and the future of civilization, against the cruelest of Society's "
        "elite."
    ),
    "golden_son": (
        "As a Helldiver, a pilot mining Mars's hellish core, Darrow proved his "
        "mettle. Now, as a Gold, he infiltrates the upper echelons of the "
        "Society he was born to destroy. With the help of the Sons of Ares, an "
        "underground revolutionary movement, Darrow climbs through Gold ranks "
        "toward the position from which he can shatter the system. But the war "
        "he wages will be one of empire and intimacy, of betrayed friendships "
        "and political schemes that will rip the Society to pieces."
    ),
    "morning_star": (
        "Darrow returns to the surface scarred and remade, ready to ignite the "
        "rebellion that has been building under the boot of Gold rule. With "
        "armies forming in the shadows and old allies counted as enemies, "
        "Darrow must unite the rebellion he never asked to lead and stand "
        "against an empire whose grip on humanity reaches across the worlds. "
        "The trilogy closes with the war Darrow has been promising since the "
        "valleys of Mars first swallowed his wife's song."
    ),
    "iron_gold": (
        "A decade after the rebellion toppled the Society, the Solar Republic "
        "is fraying at every seam. Old enemies regroup on the Rim. New "
        "factions, born of revolution and grievance, want their share of the "
        "world Darrow won. Across four points of view, the war that ended "
        "becomes the harder war that follows: keeping a republic alive when "
        "every choice creates new monsters. The Reaper, Lyria of Lagalos, "
        "Ephraim ti Horn, and Lysander au Lune each pick up a piece."
    ),
    "dark_age": (
        "The fragile Solar Republic cracks. Darrow, an outlaw to his own "
        "people, presses a brutal campaign on Mercury against a resurgent "
        "Society; Virginia holds a Republic that no longer trusts her; "
        "Lysander au Lune steps from heir to architect; and the Rim and the "
        "Core close on Earth in moves no side will survive intact. Pierce "
        "Brown's fifth Red Rising volume is a war book and a tragedy in equal "
        "measure, told across five voices."
    ),
    "light_bringer": (
        "After the catastrophes of Dark Age, Darrow is lost in the storms of a "
        "shattered Republic, his armies broken, his name a curse on a hundred "
        "worlds. To pull the Republic from the dark, he must find his way home "
        "across enemy lines and decide, again, what kind of man the Reaper has "
        "to become. Sixth in the Red Rising saga: a return to a single guiding "
        "voice, and to the long road toward what comes after the war."
    ),
    "sharp_ends": (
        "Sharp Ends gathers award-winning tales and exclusive new short stories "
        "from the world of the First Law. Across thirteen sharp, savage, and "
        "blackly funny pieces, old favorites are seen in a new light and fresh "
        "rogues are introduced, from the self-styled best thief in Styria and "
        "Javre, Lioness of Hoskopp, to a young Colonel Glokta and a battle-weary "
        "Curnden Craw. Violence explodes, treachery abounds, and nobody, as ever, "
        "is safe."
    ),
    "snow_crash": (
        "Hiro Protagonist delivers pizza for the Mafia in a near-future America "
        "fractured into corporate franchise-states. When a mysterious new street "
        "drug called Snow Crash starts crashing the brains of his hacker friends, "
        "Hiro and the teenage Kourier Y. T. find themselves chasing an "
        "information-age plague that threatens both the virtual Metaverse and the "
        "real world. Stephenson's seminal cyberpunk novel is a kinetic, satirical "
        "romp through religion, linguistics, and code."
    ),
    "the_devils": (
        "Brother Diaz arrives at the Holy City expecting a grand assignment. "
        "Instead he is handed command of the Chapel of the Holy Expediency: a "
        "cursed knight, a pirate, a werewolf, a vampire, a magician, and an elf, "
        "the worst killers and monsters the Church can muster. Their task is to "
        "escort a foul-mouthed thief across a war-torn continent and put her on "
        "the throne of Troy, uniting the sundered Church against the coming "
        "apocalypse. If they don't kill each other first."
    ),
    "the_heroes": (
        "They say Black Dow is the bloodiest tyrant ever to claw his way to power "
        "in the North, and the Union army has crossed the border to stop him. "
        "Over three brutal days of battle, in the valley of the Heroes, the fate "
        "of the North will be decided. But with both sides riddled by intrigue, "
        "ambition, cowardice, and surprise, it is unlikely to be the noblest "
        "hearts or the strongest arms that prevail. Three men. One battle. No "
        "heroes."
    ),
    "the_lesser_dead": (
        "New York City in 1978 is a dirty, dangerous place to live and die. Joey "
        "Peacock has spent forty years as an adolescent vampire perfecting his "
        "routine, womanizing in punk clubs and discotheques, feeding by night and "
        "sleeping by day in the macabre labyrinth under the city's sidewalks. "
        "Then he sees them hunting on his beloved subway: children with merry "
        "eyes, undead like him, but not at all like him."
    ),
    "witcher_last_wish": (
        "Geralt of Rivia is a witcher, born of arcane mutation and trained from "
        "childhood to slay monsters for coin. Resting in a temple between "
        "contracts, he turns over recent encounters with banshees and djinns, "
        "kings and sorceresses, in a sequence of interlinked stories that "
        "introduces the brooding antihero of a global phenomenon."
    ),
    "world_war_z": (
        "The Zombie War came unthinkably close to eradicating humanity. This is "
        "the only record of the pandemic, told in the voices of the men and women "
        "who lived through it. Driven by the urgency of preserving their "
        "firsthand testimony, Max Brooks traveled the globe, from decimated "
        "cities that once held thirty million souls to the most remote corners of "
        "the planet, recording the accounts of those who came face to face with "
        "the living dead. The result is at once a chilling chronicle of survival "
        "and a stark portrait of the world the Zombie War left behind."
    ),
}
