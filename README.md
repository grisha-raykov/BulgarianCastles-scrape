# BulgarianCastles-scrape

A Python-based web scraping project that collects and stores data about Bulgarian castles from a WordPress website into a PostgreSQL database.

## Description

This project scrapes information about Bulgarian castles from a dedicated WordPress site and stores the data in a structured format in a PostgreSQL database. It's designed to create a comprehensive dataset of Bulgarian castles for further analysis and presentation.

## Features

- Web scraping of Bulgarian castle information
- Data cleaning and processing
- PostgreSQL database storage
- Modular structure for easy maintenance and expansion

## Future Plans

We have exciting plans to enhance this project:

1. **Interactive Map Display**: Implement a feature to display all scraped castles on an interactive map.
2. **Extensive Filtering Options**: Add filtering capabilities to the map, including:
   - Accessibility (how easy it is to reach the castle)
   - Historical period
   - State of preservation
   - Visitor amenities
3. **User Contributions**: Allow users to add photos, reviews, and additional information about the castles.
4. **Mobile App**: Develop a mobile application for easy access to castle information on the go.
5. **API Development**: Create an API to allow other developers to access and use the castle data.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/grisha-raykov/BulgarianCastles-scrape.git
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your PostgreSQL database and update the connection details in `config.py`.

## Usage

Run the main script to start the scraping process:
