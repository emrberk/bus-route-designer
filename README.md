# Bus Route Designer

A short description of the project.

## Table of Contents

- [Requirements](#requirements)
- [Usage](#usage)
- [Contributing](#contributing)
- [Content](#content)

## Requirements

* Python 3.11

## Usage

* Go into the project

  ```sh
   cd bus-route-designer
  ```

* run Demo.py document from IDE or terminal with
  ```sh
   python3 DemoApp.py
  ```

## Contributing

* Emirhan Ay (e2309656)
* Emre Berk Kaya (e2380590)

## Content

1. In bus-route-designer folder, there are 2 apps, DemoApp is the demo program
   for bus route designer, and Main.py is only for testing purposes.
2. All required files are into the "src/" directory.
3. Under the "src/user", there is User.py which handles the user operations such as creation,
   deletion of users. Also, this file includes login-logout features.
4. Under the "src/util" directory, there are some static functions and validator functions.
5. Under the "src/" following documents are explained :
    * BusStop.py -> Includes stop information and related functionalities.
    * Line.py -> Includes Line information.
    * Map.py -> Includes map information and many functionalities such as shortest (which finds
      the shortest distance between two point) etc. One of the most important document in project.
    * Point.py -> Describes mathematical point object.
    * Route.py -> Includes route infos.
    * Schedule.py -> Includes all the schedule infos and operations on them.
      Another important file is that. It performs such operations as calculating estimated times
      for stops etc.
   