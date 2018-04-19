# -*- coding: utf-8 -*-
import argparse
import sys
import logging as log
import cfg
import os

# BEGIN MAIN

def main():
    parser = argparse.ArgumentParser(description='Ferramenta de anotação do PhySketch Dataset')
    parser.add_argument("-a", "--annotator", help="Executa processo de anotação", action='store_true')
    parser.add_argument("-c", "--cropper", help="Executa processo de recorte de base", action='store_true')
    parser.add_argument("-z", "--viewer", help="Executa processo de visualização de base", action='store_true')
    parser.add_argument("-g", "--generator", help="Executa processo de geração de cenário", action='store_true')
    parser.add_argument("-i", "--input", help="Pasta contendo estrutura /Dataset", required=True)
    parser.add_argument("-s", "--startAt", help="Pula -s imagens", default=0, type=int)
    #parser.add_argument("-o", "--output", help="Pasta de destino", required=True)
    parser.add_argument("-v", "--verbose", help="Verbose", action='store_true')
    args = parser.parse_args()

    cfg.START_AT = args.startAt

    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    if args.annotator:
        import annotator as an
        cfg.OUTPUT_DIR = os.path.join(args.input, "annotated")
        cfg.INPUT_DIR = os.path.join(args.input, "cropped")
        ant = an.Annotator()
        ant.run()
    elif args.cropper:
        import cropper as cr
        cfg.INPUT_DIR = os.path.join(args.input, "raw")
        cfg.OUTPUT_DIR = os.path.join(args.input, "cropped")
        ant = cr.Cropper()
        ant.run()
    elif args.viewer:
        import viewer as vw

        cfg.INPUT_DIR = os.path.join(args.input)

        vw = vw.Viewer()
    elif args.generator:
        import scene_generator as sc
        cfg.OUTPUT_DIR = os.path.join(args.input, "generated")
        cfg.INPUT_DIR = os.path.join(args.input)

        sc = sc.SceneGenerator()

    else:
        log.error("ERRO: SELECIONE UM PROCESSO")



if __name__ == '__main__':
    main()


# END MAIN
