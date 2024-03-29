import os
from zeroinstall.injector import namespaces
from zeroinstall.injector.reader import InvalidInterface, load_feed
from xml.dom import minidom, Node, XMLNS_NAMESPACE
import tempfile
from logging import warn, info

group_impl_attribs = ['version', 'version-modifier', 'released', 'main', 'stability', 'arch', 'license', 'doc-dir', 'self-test', 'langs', 'local-path']

known_elements = {
	'interface' : ['uri', 'min-injector-version', 'main'],	# (main is deprecated)
	'name' : [],
	'summary' : [],
	'description' : [],
	'needs-terminal' : [],
	'homepage' : [],
	'category' : ['type'],
	'icon' : ['type', 'href'],
	'feed' : ['src', 'arch'],
	'feed-for' : ['interface'],

	'group' : group_impl_attribs,
	'implementation' : ['id'] + group_impl_attribs,
	'package-implementation' : ['package', 'main', 'distributions'],
	'manifest-digest' : ['sha1new', 'sha256'],
	'command' : ['name', 'path', 'shell-command'],
	'arg' : [],

	'archive' : ['href', 'size', 'extract', 'type', 'start-offset'],
	'recipe' : [],
	'requires' : ['interface', 'use'],
	'runner' : ['interface', 'use', 'command'],
	'version' : ['not-before', 'before'],
	'environment' : ['name', 'insert', 'value', 'default', 'mode'],
	'executable-in-var' : ['name', 'command'],
	'executable-in-path' : ['name', 'command'],
	#'overlay' : ['src', 'mount-point'],
}

def checkElement(elem):
	if elem.namespaceURI != namespaces.XMLNS_IFACE:
		info("Note: Skipping unknown (but namespaced) element <%s>", elem.localName)
		return	# Namespaces elements are OK

	if elem.localName not in known_elements:
		warn("Unknown Zero Install element <%s>.\nNon Zero-Install elements should be namespaced.", elem.localName)
		return
	
	known_attrs = known_elements[elem.localName]

	for (uri, name), value in elem.attributes.itemsNS():
		if uri == XMLNS_NAMESPACE:
			continue	# Namespace declarations are fine

		if uri:
			info("Note: Skipping unknown (but namespaced) attribute '%s'", name)
			continue

		if name not in known_attrs:
			warn("Unknown Zero Install attribute '%s' on <%s>.\nNon Zero-Install attributes should be namespaced.",
					name, elem.localName)
		
	for child in elem.childNodes:
		if child.nodeType == Node.ELEMENT_NODE:
			checkElement(child)

def check(data, warnings = True, implementation_id_alg=None, generate_sizes=False):
	fd, tmp_name = tempfile.mkstemp(prefix = '0publish-validate-')
	os.close(fd)
	try:
		tmp_file = file(tmp_name, 'w')
		tmp_file.write(data)
		tmp_file.close()
		try:
			feed = load_feed(tmp_name, local=True, implementation_id_alg=implementation_id_alg, generate_sizes=generate_sizes)
		except InvalidInterface, ex:
			raise
		except Exception, ex:
			warn("Internal error: %s", ex)
			raise InvalidInterface(str(ex))
	finally:
		os.unlink(tmp_name)
	
	if warnings:
		doc = minidom.parseString(data)
		checkElement(doc.documentElement)

	return feed
