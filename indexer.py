

# --------------------------------------------------------------------------------------------------------------
import sys
import traceback


class EventIndex:
    def __init__(self):
        self.uuid = ''
        self.since = 0.0
        self.until = 0.0
        self.event = None
        self.abstract = ''

        self.uri_web = ''
        self.uri_file = ''

    def time(self) -> float:
        return self.since

    def adapt(self, since: float, until: float):
        return (since < self.since < until) or (since < self.until < until)

    def index_for(self, event, file: str = None, url: str = None):
        self.uri_web = url
        self.uri_file = file

        self.uuid = event.uuid()
        self.since = event.since()
        self.until = event.until()
        self.event = event

        if event.title() is not None and event.title().strip() != '':
            self.abstract = event.title()
        elif event.brief() is not None and event.brief().strip() != '':
            self.abstract = event.brief()
        elif event.brief() is not None and event.brief().strip() != '':
            self.abstract = event.event()
        self.abstract = self.abstract.strip()[:50]


class EventIndexer:
    def __init__(self):
        pass

    def index_for_events(self, events: list):
        pass

    def index_for_path(self, directory: str):
        pass

    def set_index_prefix(self, prefix: str):
        pass



def test():
    import os
    import os.path

    # this folder is custom
    rootdir = "D:"
    for parent, dirnames, filenames in os.walk(rootdir):
        print(str(parent) + ' | ' + str(dirnames) + '|' + str(filenames))
        # # case 1:
        # for dirname in dirnames:
        #     print("parent folder is:" + parent)
        #     print("dirname is:" + dirname)
        # # case 2
        # for filename in filenames:
        #     print("parent folder is:" + parent)
        #     print("filename with full path:" + os.path.join(parent, filename))




def main():
    test()


# ----------------------------------------------------------------------------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


if __name__ == "__main__":
    sys.excepthook = exception_hook
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass


