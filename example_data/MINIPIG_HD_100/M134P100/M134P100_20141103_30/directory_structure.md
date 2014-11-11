# Explanation of the chosen file structure

As suggested in the Directory Organization For MINIPIG Collaboration
document, I've now set up a file structure for the minipig project
according to the rules.

### Project Tier

> ${PROJECT} is a placeholder for project - These need globally
> unique. There will likely be only one project right now (i.e.
> MINIPIG_HD_100)

The project ID set to *MINIPIG_HD_100*

### Subject Tier

> ${SUBJECT} is a placeholder for the subject - These need to be
> globally unique for all subjects. You MAY NOT re-use a subjectID in
> multiple projects.

The subject IDs are constructed by
- M for minipig
- a three digit number unique for each pig, which is actually their ear
mark nuber. This is actually not a pseudonyme, but we do not have to
anonymize the data
- P for project
- the three digit project ID, ensuring the name to be unique in each
  project
  

### Session Tier

> ${SESSION} is a placeholder for the session - These need to be
> globally unique. The SESSION must uniquely identify this session and
> this ID may not be re-used in any other project or for any other
> session.

The session ID format was chosen to be *${SUBJECT}\_${DATE}\_${TESLA}* as
suggested, (M${ID1}P${ID2}_${DATE}_30). We'll never use something else than
a 3 Tesla scanner, though.

SUBJECT=M${ID1}P${ID2} where 

ID1 is the unique earmark given to each pig and 

ID2 is the unique number of the project that the pig was primarily assigned to.

DATE=YYYYMMDD where YYYY, MM, DD represents the Year/Month/Day of the scan sessions respectively.

30=indicates that these are 3T scanner sequences.
