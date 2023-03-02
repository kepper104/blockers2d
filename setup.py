import pip


def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])


install('pygame')
install('packages/noise-1.2.3-cp38-cp38-win_amd64.whl')
install('pygame_widgets')