# LISA
### [Project Video](https://youtu.be/yHcJJCffDqk)
### Description
LISA (Logic-based, Interactive, Synthetic Assistant) is a digital personal assistant I created to unify the various parts of my digital life. She communicates with users by texting them using the `twilio` library.

The iteration posted here is capable of turning my lights on and off, checking their status with a webcam, playing music on my computer, and having natural language conversations with the help of the `pyaiml` library. It's incredibly easy to integrate any other python program into her repertoire, so she could check grades, play a sound on a lost phone, change the temperature on an internet connected thermostat, etc. She also knows who she's talking to, and can determine whether or not to allow users to execute functions based on their permissions. Admin users can generate codes that allow for single uses of restricted functions by talking to LISA and providing the intended user's phone number.

### Highlights
- Basic Natural Language Processing with `nltk`
- Image Analysis with `OpenCV`
- Runs as a `cherrypy` webserver
- Integration with `twilio` for user interaction
- Modular functionality

### Disclaimer
The iteration of LISA posted here relies strongly on integration with specific aspects of my server environment (including a database which isn't currently posted), and isn't intended to be downloaded and run on other machines (although people can certainly try if they want!). A less environment-specific version of the project is in the works.


