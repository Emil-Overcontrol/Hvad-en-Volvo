# Hvad en Volvo
Jeg har fået til opgave at indplementere ting som søgeside, database, menu, dokumentationside, styling og udover kan du også lave en loginside og noget javascript hvis du kar lyst til at lave mere ud over end hvad du har prøvet. Her kommer du til at kunne gætte den bil i form af en Volvo da dette er fårmålet ved denne hjemmeside er kan du gette denne bil som hjemmeside (websveren) har fundet / valgt. ja som sagt tidliger dette kommer til at en websever hvor man kommer til at deltage i. Du skulle komme til at sætte alle Volvo’s bilmodeller så alt fra som 244 eller de nye s80, grunden til jeg har valgt at lave denne hjemmeside er at jeg kan godt lide Volvo biler (mest de gamle) men vil staig udfortre mig selv når det kommer til at kende deres forskælillege årgangsmodeller. Det hville være sådan når man ligsom man ser på den når man getter at der er et stykke, hvor mere bilen bilver afsløret af billedet bliver mere og mere synligt samt de hints du får som er med til at få dig til at gætte bilen

## Volvo-database

Webserveren bruger SQLite og opretter automatisk `Websever_hvad_den_Volvo/volvo.sqlite3`,
første gang Flask-appen starter. Databasen har separate tabeller for:

- `car_models`: Volvo-modellen, for eksempel `240` eller `S80`
- `colors`: farver
- `model_colors`: hvilke farver der hører til hver model
- `model_years`: de år, hvor modellen blev solgt

Data kan hentes fra API'et:

- `GET /api/cars` henter alle modeller
- `GET /api/cars/240` henter én model

Volvo-modellerne ligger separat i `Websever_hvad_den_Volvo/car_data.py`,
på samme niveau som `app.py`. Seed-dataen indeholder Volvos vigtigste modelserier fra PV, Amazon og P1800
til 140/164, 240/700/900, 850, S/V/C/XC-serierne og de nyere EX/EC-elbiler.
