from typing import List


class Prompt:
    prompt: str

    def __init__(
        self,
        job_description: str,
        candidate_name: str,
        candidate_description: str,
        candidate_work_experience: List[str],
        candidate_age: str,
        candidate_country: str,
    ):
        self.prompt = f"""You are a professional recruiter with 10 years of experience. Help me write a letter to a job candidate, to make him interested in this position.
Here is the job description:
{job_description}
Here is information about the candidate:
{candidate_name}
{candidate_description}
Here is candidate’s experience:"""
        for i, job in enumerate(candidate_work_experience):
            self.prompt += f'\nRole {i+1}:\n{job}'
        self.prompt += f"""\nHelp me write a higly personalized LinkedIn message for this candidate that resonates with him and makes him interested in this job. Keep in mind these requirements:
- the candidate is {candidate_age} years old from {candidate_country}, tailor the message specifically for him, but DO NOT mention the age
- KEEP THE MESSAGE NOT MORE THAN 300 SYMBOLS!
- add a hook or a joke that appeals to those who work in candidate's industry
- IMPORTANT: MAINTAIN A BALANCE BETWEEN A FORMAL TONE AND JOKES; DON'T BE TOO BORING, BUT ALSO DON'T BE TOO SILLY OR FUNNY

- never write cliches like "Best regards" or "Kind regards". make it sound more personal
- IMPORTANT: insert candidate name NOT in a cliche way. NEVER INSERT NAME OF THE RECRUITER IN THE END

- try to sell candidate on the position, but DO NOT be too pushy
- in the end ask if candidate wants to discuss this position further
Follow this structure:
“Greetings. A bright or catchy phrase or joke from the candidate's professional area. Why I was attracted to their resume. What I bring to the candidate (job / vacancy). The question is whether he is ready to continue the dialogue (please ask only one question; avoid clichéd marketing phrases)”"""
        self.prompt += """\nHere are some examples of good letters that we've already written. TRY YOUR BEST TO MAKE IT IN SIMILAR STYLE.

Hey Mark,
Stumbled upon your background and couldn't help but get a bit geeky-excited at the Django-to-Kubernetes spectrum you've mastered! We're ITkey, a player in OpenStack solutions, and we're on the hunt for a Python Developer. Your skills in Python, FastAPI, and Kubernetes are right up our alley. 
How about swapping your current scenery with large-scale, high-load projects and a team of top-tier professionals? 

Hey Anna,
I've been exploring the galaxies of LinkedIn and found your star brilliantly shining in the Python universe. I am from Itkey and we're brewing a Python Developer position. It’s all about OpenStack Solutions.
Fancy learning more over a chat?

Hi Igor,
Caught me with your Python skills, mate! I am from ITkey and we're brewing a Python Developer position. It’s all about OpenStack Solutions.
I believe your expertise в Яндексе (немного русского в этом чатике) fits like a glove. 
Fancy learning more over a chat?

Hi Jeff,
Caught me with your Python skills! I am from ITkey and we're brewing a Python Developer position (it’s remote so you can work from any point on Earth that has Wi-Fi) and involves working on high-load, large-scale projects.Let's chat more about this, shall we?

These are examples. Now write a letter according to all given instructions. TRY YOUR BEST TO MAKE IT IN SIMILAR STYLE. MAKE THE MESSAGE PERSONALIZED. DON'T SAY GOODBYE, CHEERS OR ANY OTHER CLICHE IN THE END.
"""