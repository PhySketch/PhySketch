class Annotator:
    listSamples = []

    def __init__(self):

        for item in os.listdir(cfg.INPUT_DIR):
            if not item.startswith('.') and os.path.isfile(os.path.join(cfg.INPUT_DIR, item)):
                self.listSamples.append(Sample(os.path.join(cfg.INPUT_DIR, item)))

    def run(self):
        return