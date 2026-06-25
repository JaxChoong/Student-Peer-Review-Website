# Fix Propshaft serving JavaScript files with wrong MIME type (text/plain).
# Propshaft uses Rails' Mime::Type registry, not Rack::Mime.
# We register "js" explicitly so it resolves to application/javascript.
Mime::Type.register "application/javascript", :js unless Mime::Type.lookup_by_extension(:js)
