# Final-Project-Novel-Webscraper
This project scrape web-novels from the website and convert them into an Epub file extension.

> Exit the program at anytime using ctrl+c

# Steps
1. Run the project.py
2. Choose browing method between:
   * Full Novel List by entering "1":
     * Browse the list and copy the id of chosen novel or just memorize it
     * Exit the txt file
     * Enter the copied or memorized id of the selected novel

   * Search by entering "2":
     * Enter complete or partial name of novel but it's spelling has to correct.
     * Then result of search will be printed with id unique to the novels
     * Then enter the id of novels from the printed list

3. Proceeding forword, enter starting chapter and ending chapter of the novel epub file.
   * The starting and ending chapter should not exceeding the latest chapter number.

4. The program will scrape the novel and pack them in to chapter.html
5. More files necessary for epub extention will be zipped together with chapters and its extention will be renamed to epub.
6. Unnecessary files will be removed.
7. At the last step, either proceed with scrape more novels or exit the program with ctrl+c.
