import html

from twisted.internet import reactor
from twisted.web import resource, server


class Simple(resource.Resource):
    isLeaf = True

    def render(self, request):
        """
        request.args.get('key', '') gets the forms values.  This
        "page" just prints a SUBMIT button and a text field.

        There is no actual CGI called "default.cgi",  you would have
        to handle seperate script files manually at this stage,  but
        you could handle your forms page right here.  In this example
        I have a textfield called "Field" as you see in the HTML below.

        when submitting,  this just loops back to this code,  extracts
        the forms values,  then re-renders the forms page in html before
        it exits and loops back again.
        """
        IP = request.getClientIP()
        out_html = ""
        out_html += "<html>Hello, world!</html><br><br>"
        out_html += "Keys are...<br>"
        for key in request.args.keys():
            out_html += "%s " % html.escape(str(key))
        out_html += "<br>uri = %s<br>" % html.escape(str(request.uri))
        out_html += "<br>method = %s<br>" % html.escape(str(request.method))
        out_html += "<br>path = %s<br>" % html.escape(str(request.path))

        field_value = request.args.get("Field", "")
        out_html += "<br>Field = %s<br>" % html.escape(str(field_value))
        out_html += "<br>ClientIP = %s<br>" % html.escape(str(IP))
        button_val = request.args.get("name_submit", "")
        out_html += "<br>button_val = %s<br>" % html.escape(str(button_val))
        form = """
        <FORM ACTION="." METHOD="POST" ENCTYPE="application/x-www-form-urlencoded">
<P>Test input: <INPUT TYPE="TEXT" NAME="Field" SIZE="25"><BR>
<INPUT TYPE="SUBMIT" NAME="name_submit" VALUE="Submit">
</FORM>
        """
        return out_html + form


if __name__ == "__main__":
    site = server.Site(Simple())
    reactor.listenTCP(8000, site)
    reactor.run()
