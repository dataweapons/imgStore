#!/usr/bin/env python3
import logging
import glob
import itertools
from time import ctime
from os.path import dirname, join, abspath
from os import chdir, getcwd
from sys import exit
from subprocess import check_call
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
import click

cwd = getcwd()
chdir(dirname(__file__))


from common.raven import get_client, general  # noqa
from common.config import get_state, on_mountpoint, TEMPDIR, config, SENTRY  # noqa

client = get_client(dsn=general)
stream_handler = logging.StreamHandler()
stream_handler.level = logging.WARNING
logging.basicConfig(
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        handlers=[logging.FileHandler(join(TEMPDIR, "Combiner.log")),
                  stream_handler])

logger = logging.getLogger("main")
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
        logging.WARNING)
logging.getLogger("datastore").setLevel(logging.WARNING)

MISSING_PNG = abspath(join(dirname(__file__), "resources", "Missing.png"))


def preprocess_images(image_filenames):
    """
    Manually convert any xwd files to a png,
    as Pillow can't handle xwd files.
    Returns an iteration of filenames to use
    """
    for image_filename in image_filenames:
        if image_filename is None:
            continue
        if image_filename.endswith(".xwd"):
            new_filename = image_filename.replace(".xwd", ".png")
            try:
                check_call(["gm", "convert", image_filename, new_filename])
                yield new_filename
            except:
                yield MISSING_PNG
        else:
            yield image_filename


@click.command()
@click.option('--mrn', prompt=False)
@click.option('--poi', prompt=False)
@click.option('--output', prompt=False)
@click.option('--subtext', prompt=False)
@click.option('--name', prompt=False)
@click.option('--dob', prompt=False)
@click.argument('inputs', nargs=-1)
def point(mrn, poi, output, subtext, inputs, name, dob):
    try:
        assert mrn is not None
        assert output is not None
        assert output.endswith(".pdf")
        c = canvas.Canvas(join(cwd, output), pagesize=A4)
        c.drawString(x=0 * cm, y=28 * cm,
                     text="MRN: {}".format(mrn))
        if name is not None:
            c.drawString(x=10 * cm, y=28 * cm, text="Name: {}".format(
                name.upper()))
        if dob is not None:
            c.drawString(x=4.5 * cm, y=28 * cm, text="Date of Birth: {}".format(
                dob.upper()))
        if poi is not None:
            c.drawString(x=0 * cm, y=27.5 * cm, text="POI: {}".format(
                poi.upper()))
        if subtext is not None:
            c.drawString(x=10 * cm, y=27.5 * cm, text=subtext)
        c.drawString(x=15 * cm, y=.5 * cm, text=ctime())

        c.setFont("Helvetica", 24)
        for i, image_filename in enumerate(reversed(list(preprocess_images(
                inputs)))):
            title = image_filename.rsplit('/', 1)[-1].rsplit(".", 1)[0].upper()
            c.drawString(x=1 * cm,
                         y=(9 * i + 8) * cm,
                         text=title)
            c.drawImage(join(cwd, image_filename),
                        x=6 * cm,
                        y=(9 * i + 1) * cm,
                        width=15 * cm,
                        height=8 * cm,
                        preserveAspectRatio=True,
                        anchor="c")
        c.showPage()
        c.save()
    except Exception:
        if SENTRY:
            client.captureException()
        raise
    exit(0)


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


@click.command()
@click.option('--mrn', prompt=False)
@click.option('--output', prompt=False)
@click.option('--subtext', prompt=False)
@click.option('--name', prompt=False)
@click.option('--dob', prompt=False)
@click.argument('inputs', nargs=-1)
def beam(mrn, output, subtext, inputs, name, dob):
    try:
        if len(inputs) == 1:
            inputs = glob.glob(inputs[0])
            logger.info("Globbed inputs: {}".format(str(inputs)))
        assert mrn is not None
        assert output is not None
        assert output.endswith(".pdf")
        for page_number, page_inputs in enumerate(grouper(inputs, n=4)):
            c = canvas.Canvas(join(cwd, "{}-{:02d}.pdf".format(output[:-4],
                              page_number)), pagesize=A4)
            c.drawString(x=0 * cm, y=28 * cm,
                         text="MRN: {}".format(mrn))
            if name is not None:
                c.drawString(x=10 * cm, y=28 * cm, text="Name: {}".format(
                    name.upper()))
            if dob is not None:
                c.drawString(x=4.5 * cm, y=28 * cm, text="Date of Birth: {}".format(
                    dob.upper()))
            if subtext is not None:
                c.drawString(x=10 * cm, y=27.5 * cm, text=subtext)
            c.drawString(x=15 * cm, y=.5 * cm, text=ctime())

            c.setFont("Helvetica", 18)
            for i, image_filename in enumerate(list(preprocess_images(
                    page_inputs))):
                x = ((i % 2) * 10) * cm
                y = (14 - 12 * (i // 2)) * cm
                beam_name = image_filename.split("/")[-1].rsplit(".", 1)[0]
                c.drawString(x=x + 1 * cm, y=y + 10.2 * cm, text=beam_name)
                c.drawImage(join(cwd, image_filename),
                            x=x, y=y,
                            width=10 * cm,
                            height=10 * cm,
                            preserveAspectRatio=True,
                            anchor="c")
            c.showPage()
            c.save()
    except Exception:
        if SENTRY:
            client.captureException()
        raise
    exit(0)

