#!/usr/bin/python

import web
from myQuad import CopterDataReader

urls = (
'/', 'index'
)

copterDataReader = CopterDataReader()


class index:
    def GET(self):
        axes = copterDataReader.get_rotation_angles()
        return str(axes['x']) + " " + str(axes['y']) + " " + str(axes['z'])


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

