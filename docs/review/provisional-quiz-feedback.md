# Provisional quiz feedback for review

**Status:** Provisional practice feedback, not the official Google Forms answer key.
The supplied quiz PDFs list questions and point values but do not identify correct choices or explanations. These proposed choices were inferred from the supplied course slides and question wording. Do not use them as an official assessment key until a course owner reviews them.

The learner-facing library is `content/readings/ucsf/u00-n02-version3-form-library.ipynb`. Edit `course-materials/version3-quiz-feedback.json` to correct a proposed choice or explanation, then regenerate the notebook and this review sheet.

**Priority review:** Unit 2 question 2 says ‘select all’ although this provisional key has one choice; Unit 5 questions 1–2 depend on the course's distinction between PII, PHI, and other sensitive data; Unit 7 question 2 offers a drop-down but no explicit yes/no radio control. Please confirm those items against the form owner's key first. [CDC guidance](https://www.cdc.gov/niosh/ocas/datahandle.html) and [HHS guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html) treat biometric identifiers as identifying in relevant contexts, so Unit 5's slide category should not be generalized.

## Unit 1

### Question 1: How do advances in information and computer science enhance public health surveillance for epidemiologists?

**Proposed choice:** 2. They improve data collection, quality, and analysis for faster interpretation.

**Feedback:** Better collection, quality, and analysis help epidemiologists interpret reports sooner; people still judge the evidence and decide what to do.

### Question 2: Which of the following are essential capabilities for a public health organization to become an Informatics-Savvy Health Organization (ISHO)?

**Proposed choices:** 3. Organization-wide informatics vision, policy, and governance; 4. Effective, interoperable information systems; 5. A skilled workforce

**Feedback:** An informatics-savvy organization needs governance, interoperable systems, and people with the skills to use them.

### Question 3: The Data-Information-Knowledge-Wisdom Pyramid describes how raw data is transformed into meaningful insights for action. Fill in the blank with the correct layer of the pyramid: ________ is gained when epidemiologists and informaticians analyze information using their understanding of diseases, populations, and environments.

**Proposed choice:** 1. Knowledge

**Feedback:** Knowledge comes from interpreting information with disease, population, and setting expertise. Wisdom is the informed action that follows.

### Question 4: Which of the following best defines public health informatics?

**Proposed choice:** 3. The science of using data, information, and knowledge to improve human health and healthcare delivery.

**Feedback:** Public health informatics uses data, information, and knowledge to improve health and care delivery.

## Unit 2

### Question 1: Which of the following key strategic areas commonly found in a country's Health Information System (HIS) Strategy is most likely to directly impact epidemiologists' work?

**Proposed choice:** 2. Integration of health information systems

**Feedback:** Integrating health information systems changes how epidemiologists can find and combine the reports they need.

### Question 2: What do surveillance systems and health information systems have in common?

**Proposed choice:** 4. They both routinely collect data about events and cases.

**Feedback:** Both systems routinely collect reports about events and cases across levels of the health system.

### Question 3: What is one reason why epidemiologists might see a sudden spike in case numbers on surveillance dashboards?

**Proposed choice:** 3. The use of multiple software applications causes delays in data reporting, leading to backlogs being cleared all at once.

**Feedback:** A backlog cleared after delayed reporting can create a dashboard spike even when events did not suddenly increase.

### Question 4: Poor network connectivity is an example of technology infrastructure issues that can interfere with:

**Proposed choice:** 4. All of the above

**Feedback:** Poor connectivity can interrupt collection, reporting, and access to the resulting data.

### Question 5: What is essential for keeping health software applications running, beyond improving IT infrastructure?

**Proposed choice:** 3. Provide help desk staff, systems, and procedures to support users and troubleshoot technical issues

**Feedback:** User support, help desk procedures, and troubleshooting keep applications usable after deployment.

### Question 6: Which of the following data responsibilities is typically assigned to clinical staff within a health information system?

**Proposed choice:** 1. Collecting and recording accurate patient information during care

**Feedback:** Clinical staff record accurate patient information during care; national policy and warehouse management have different owners.

## Unit 4

### Question 1: Which of the following are sources of secondary data that epidemiologists can use for surveillance and outbreak investigations?

**Proposed choices:** 1. A national demographic survey report from two years ago; 2. A health facility report summarizing case data based on patient records; 4. Laboratory test results extracted from an existing electronic laboratory information system

**Feedback:** Existing survey reports, facility summaries, and laboratory extracts are secondary sources for this investigation. Newly collected investigation data and the new focus group are primary sources.

### Question 2: True or False: When selecting health information system software as a source of secondary data, it is important to consider whether or not the data is relevant to your information needs.

**Proposed choice:** 2. True

**Feedback:** A secondary source is useful only if its people, place, time, and variables fit the information need.

### Question 3: Which of the following statements correctly describe the difference between a feature and a function in health information systems?

**Proposed choices:** 1. A feature is a general capability; a function is a specific task the system can do.; 3. A feature is something the system offers, like mapping tools or dashboards.; 4. A function is an action the system performs, like generating a report.

**Feedback:** A feature is a general capability such as mapping; a function is an action such as generating a report.

### Question 4: Which of the following are characteristics of a good feature request when working with health information system developers or vendors?

**Proposed choices:** 1. It clearly describes the problem the user is trying to solve.; 3. It explains how the feature would support specific tasks or decisions.; 5. It provides examples or screenshots, if possible, to illustrate the request.

**Feedback:** A useful request states the user problem, the task or decision it supports, and a concrete example.

## Unit 5

### Question 1: Which of the following are examples of Personally Identifiable Information (PII)?

**Proposed choices:** 1. Date of birth; 2. Marital status; 4. National ID number

**Feedback:** The supplied security slide groups date of birth, marital status, and national ID under PII; it shows HIV results as health information and biometrics as other sensitive data. Biometrics can identify people in other contexts, so this provisional choice needs course-owner review.

### Question 2: True or False: Biometric data such as fingerprints, retina scans, and facial images are considered sensitive data but are not necessarily PII or PHI.

**Proposed choice:** 1. True

**Feedback:** The course distinguishes biometric data as sensitive data that may or may not also identify a person or relate to their health in a particular setting.

### Question 3: Which of the following are possible consequences for an organization if sensitive data are not kept secure?

**Proposed choices:** 1. Erosion of public trust; 3. Lawsuits from individuals or other organizations; 4. Negative press coverage

**Feedback:** A security failure can erode trust and bring legal and reputational harm; it does not increase participation.

### Question 4: When selecting a software application, which of the following security features should you look for?

**Proposed choices:** 1. Data encryption during transmission; 2. Ability to restrict user access based on roles; 3. Automatic logout after inactivity

**Feedback:** Encryption in transit, role-based access, and inactivity logout reduce disclosure risk. Public sharing without consent does the opposite.

### Question 5: You are part of a field epidemiology team investigating a suspected cholera outbreak in a remote community. You are using a mobile data collection app to record names, addresses, symptoms, and GPS coordinates of cases. Which actions below follow good data security and confidentiality practices?

**Proposed choices:** 1. Use the app’s encryption feature to secure data during transmission.; 3. Restrict app access to only trained team members with a unique login.; 5. Store the data on a password-protected device and back it up to a secure server.

**Feedback:** Protect transmission, limit access to trained users, and secure the device and backup. Names, addresses, and GPS locations require care.

## Unit 7

### Question 1: In general, what is the most important factor when selecting a data collection software tool?

**Proposed choice:** 4. It is a tool already in use by MOH or for other similar data collection investigations

**Feedback:** Begin with an existing tool that the ministry or investigation already uses, then verify it meets the task's critical needs.

### Question 2: If a person has any symptoms or not, which question type would be best?

**Proposed choice:** 2. Drop down

**Feedback:** Of these offered controls, a drop-down can capture one yes/no choice. A symptom list allowing several answers needs checkboxes.

### Question 3: For date of symptom onset, which question type would be best?

**Proposed choice:** 3. Calendar

**Feedback:** A calendar or date picker helps capture symptom-onset dates in a consistent format.

### Question 4: For a list of symptoms where more than one choice can be indicated, which question type would be best?

**Proposed choice:** 4. Checkboxes

**Feedback:** Checkboxes let a learner or data collector select more than one symptom.

### Question 5: Validation rules are important because they can:

**Proposed choice:** 4. All of the above

**Feedback:** Validation can require answers, constrain feasible ranges, and enforce formats.

### Question 6: Piloting a new or modified digital data collection tool is important because:

**Proposed choice:** 4. All of the above.

**Feedback:** A pilot checks user fit, technical operation, and whether the tool needs changes before wider use.

### Question 7: When piloting a tool, a brief piloting plan should be created and contain (check all that apply):

**Proposed choices:** 1. Number of users who will pilot; 2. The cadre or roles of the testers; 3. Where the piloting will happen (such as name of facility or region); 5. How long the pilot will go on; 7. Definition of successful pilot, ready for scale-up

**Feedback:** Plan who will test, where and for how long, and what counts as success. Age and height are not general pilot-plan requirements.

### Question 8: What are some key considerations for confirming if a digital tool is the right fit for the project?

**Proposed choice:** 4. All of the above.

**Feedback:** Fit includes critical functions, sustainability, and whether the tool is already used or approved locally.

### Question 9: Select various considerations in sustainability of a digital data collection tool (check all that apply):

**Proposed choices:** 1. Software licenses and possible hardware costs; 2. Cost and ability to procure data bundles; 4. Costly specialized skills are required; 5. Costs for any server procurement or set-up

**Feedback:** Budget for licenses, devices, connectivity, specialist skills, and servers. Colorful charts alone are not a sustainability criterion.
