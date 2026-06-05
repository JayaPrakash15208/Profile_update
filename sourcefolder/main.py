import naukri 
import Naukari_resume_update

def profiles():
    print(f'Which profile fo you want to run:\n')
    print(f'1.ChandraSekhar\n2.Jay Prakash\n')


def runProfile(confirm):
    while confirm == 'y':
        profiles()
        profile = int(input(f'Select Profile:\t'))
        if profile == 1:
            naukri.main()
        elif profile == 2:
            Naukari_resume_update.main()
        else:
            pass
        confirm=input('Do you want select another profile? y/n:\t')
        runProfile(confirm)
    else:
        print(f'You wish to discontinue')


confirm = input('Continue to profiles y/n:\t')
runProfile(confirm)
