#!/bin/bash

wgetcmd="wget --no-check-certificate --no-use-server-timestamps --directory-prefix=libs"

# Preserve the order
$wgetcmd https://files.pythonhosted.org/packages/ca/1e/d91d7aae44d00cd5001957a1473e4e4b7d1d0f072d1af7c34b5899c9ccdf/pip-20.3.3.tar.gz
# $wgetcmd https://files.pythonhosted.org/packages/67/ab/41e4b42e0519d868347d2cf1051a05ce0170632039c053dee8ffe8b43b0b/numpy-1.8.2.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/fd/54/aee23cfc1cdca5064f9951eefd3c5b51cff0cecb37965d4910779ef6b792/numpy-1.16.6-cp27-cp27mu-manylinux1_i686.whl
$wgetcmd https://files.pythonhosted.org/packages/11/c4/2da1f4952ba476677a42f25cd32ab8aaf0e1c0d0e00b89822b835c7e654c/enum34-1.1.10.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/f8/5c/f60e9d8a1e77005f664b76ff8aeaee5bc05d0a91798afd7f53fc998dbc47/Click-7.0.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/68/1a/f27de07a8a304ad5fa817bbe383d1238ac4396da447fa11ed937039fa04b/itsdangerous-1.1.0.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/4f/e7/65300e6b32e69768ded990494809106f87da1d436418d5f1367ed3966fd7/Jinja2-2.11.3.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/b9/2e/64db92e53b86efccfaea71321f597fa2e1b2bd3853d8ce658568f7a13094/MarkupSafe-1.1.1.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/c3/1d/1c0761d9365d166dc9d882a48c437111d22b0df564d6d5768045d9a51fd0/Werkzeug-0.16.1.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/32/57/3c33fe153ea008e9e0202eb028972178337c55777686aac03f41ade671f8/Flask-0.12.5.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/59/21/6e5de34d711de50c54b4aa63b15e43b689c9b372aaed349b3fa13c9345e9/cltl.backend-naoqi-0.0.dev7.tar.gz
$wgetcmd https://files.pythonhosted.org/packages/41/96/8d1d3f0f160512d637c1aeaeddf4039525ee0eb17cf5be0c1eca7de6bd76/virtualenv-13.1.2.tar.gz

