from twisted.web import server, resource
from twisted.internet import reactor

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
        html = ""
        html += "<html>Hello, world!</html><br><br>"
        html += "Keys are...<br>"
        for key in request.args.keys():
            html += "%s " % key
        html += "<br>uri = %s<br>" % request.uri
        html += "<br>method = %s<br>" % request.method
        html += "<br>path = %s<br>" % request.path
        
        field_value = request.args.get('Field', '')
        html += "<br>Field = %s<br>" % field_value
        html += "<br>ClientIP = %s<br>" % IP
        button_val = request.args.get('name_submit','')    
        html += "<br>button_val = %s<br>" % button_val
        form = """
        <FORM ACTION="." METHOD="POST" ENCTYPE="application/x-www-form-urlencoded">
<P>Test input: <INPUT TYPE="TEXT" NAME="Field" SIZE="25"><BR>
<INPUT TYPE="SUBMIT" NAME="name_submit" VALUE="Submit">
</FORM>
        """
        return html + form

if __name__=="__main__":
    site = server.Site(Simple())
    reactor.listenTCP(8000, site)
    reactor.run()