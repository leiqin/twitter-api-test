# -*- coding: utf-8 -*-

def print_response(response):
    print '%s %s' % (response.getcode(), response.msg)
    print response.info()
    print 
    print response.read()

