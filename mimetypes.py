from xml.dom import minidom
from zeroinstall.injector import namespaces

def add_types(data):
	doc = minidom.parseString(data)
	
	changed = False
	for archive in doc.documentElement.getElementsByTagNameNS(namespaces.XMLNS_IFACE, 'archive'):
		href = archive.getAttribute('href')
		type = archive.getAttribute('type')

		if not type:
			if href.endswith('.tar.bz2'):
				type = "application/x-bzip-compressed-tar"
			elif href.endswith('.tgz') or href.endswith('.tar.gz'):
				type = "application/x-compressed-tar"
			else:
				raise Exception("Can't guess type for " + href)
			archive.setAttribute('type', type)
			changed = True

	if changed:
		return doc.toxml()
	else:
		return data
