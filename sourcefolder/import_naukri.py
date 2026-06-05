import naukri 
import Naukari_resume_update

def profiles():
    print(f'Which profile fo you want to run:\n')
    print(f'1.ChandraSekhar\n2.Jay Prakash\n')
def runProfile():
    while True:
        confirm = input('Continue to profiles y/n:\t').lower()
        if confirm != 'y':
            print('You wish to discontinue')
            break

        profiles()
        profile = int(input('Select Profile:\t'))

        if profile == 1:
            naukri.main()
        elif profile == 2:
            Naukari_resume_update.main()
        else:
            print("Invalid selection")
