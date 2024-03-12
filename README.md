# SapphireCMS

## CLI
  A CLI application for managing SapphireCMS websites. 
  - Create a new SapphireCMS installation:

    `sapphire install [-h] [-e] [name]`

     name: The name of the new SapphireCMS website
     -e, --env:   Create a new environment for this SapphireCMS website
  - Manage website configurations:

    `sapphire config [-h] [{setactive,set,get,create,list}] [id] [data]`
   
    {setactive,set,get,create,list}: The action to perform on the current SapphireCMS website
    id: Identifier of the configuration to perform the action on
   data: Data to set the configuration to (Only for action 'set')
  - Run the current SapphireCMS website:

    `sapphire run [-h] [{dev,prod}]`

    {dev,prod}:  The mode to run the current SapphireCMS website in
  - Serve the current SapphireCMS website (same as `sapphire run prod`):

    `sapphire serve [-h]`
  - Enable or disable the system service for the current SapphireCMS website:

    `sapphire service [-h] [{start,stop,restart}]`

    {start,stop,restart}: Enable or disable the system service for the current SapphireCMS website
  - Manage themes for the current SapphireCMS website:

    `sapphire theme [-h] [{add,remove,list}] [id]`

    {add,remove,list}: The action to perform on the current SapphireCMS website
    id: Identifier of the theme to perform the action on (Can be a name or a URL for adding a theme)
  - Get the version of the current SapphireCMS environment (same as pip install --upgrade sapphirecms):

    `sapphire update`
  - Get help for the SapphireCMS CLI.:

    `sapphire -h`

## Routing
A router with sub-routing and proxy-routing 
### Router
   ```python
   from sapphirecms.routing import Router, Request
   router =  Router()

   router.add_route("/hi/<name>", "GET")(lambda  request, slug: f"Hello {name}!")
   print(router.route(Request("GET /hi/User HTTP/1.1\r\n")))
   ```
### Sub-Router
   ```python
   subrouter =  Router("subsite", prefix="/web1", ctx=__name__)
   subrouter.add_route("/home", "GET")(lambda  request: f"Welcome to subsite!")
   
   router.add_subrouter(subrouter)
   
   print(router.route(Request("GET /web1/home HTTP/1.1\r\n")))
   ```
### Proxy-Router
   ```python
   from sapphirecms.routing import ProxyRouter
   
   proxyrouter =  ProxyRouter("p", internal_path="/proxy", external_path="http://someserv.er/entry/path")
   
   router.add_proxy(proxyrouter)
   
   print(router.route(Request("GET /proxy/remotepath HTTP/1.1\r\n")))
   ```

## Templating
   A Pythonic templating engine that allows you to define and modify webpages using Python with prerendering capability.

   Example:

   1. Define reuseable components
         ```python
         # type: ignore[a,abbr,address,area,article,aside,audio,b,base,bdi,bdo,blockquote,body,br,button,canvas,caption,cite,code,col,colgroup,command,datalist,dd,del,details,dfn,div,dl,dt,em,embed,fieldset,figcaption,figure,footer,form,h1,h2,h3,h4,h5,h6,head,header,hgroup,hr,html,i,iframe,img,input,ins,kbd,keygen,label,legend,li,link,map,mark,math,menu,meta,meter,nav,noscript,object,ol,optgroup,option,output,p,param,pre,progress,q,rp,rt,ruby,s,samp,script,section,select,small,source,span,strong,style,sub,summary,sup,svg,table,tbody,td,textarea,tfoot,th,thead,time,title,tr,track,u,ul,var,video,wbr]
         from sapphirecms import html
         from themes import get_active_theme
         
         html.initialize(__name__)
         theme =  get_active_theme().THEME()
         
         navigation = theme.navigation([
             ("Home", "/"),
             ("Documentation", "/docs"),
         ]
   2. Initialise templating on pages with definitions
         ```python
         # type: ignore[a,abbr,address,area,article,aside,audio,b,base,bdi,bdo,blockquote,body,br,button,canvas,caption,cite,code,col,colgroup,command,datalist,dd,del,details,dfn,div,dl,dt,em,embed,fieldset,figcaption,figure,footer,form,h1,h2,h3,h4,h5,h6,head,header,hgroup,hr,html,i,iframe,img,input,ins,kbd,keygen,label,legend,li,link,map,mark,math,menu,meta,meter,nav,noscript,object,ol,optgroup,option,output,p,param,pre,progress,q,rp,rt,ruby,s,samp,script,section,select,small,source,span,strong,style,sub,summary,sup,svg,table,tbody,td,textarea,tfoot,th,thead,time,title,tr,track,u,ul,var,video,wbr]
         from sapphirecms import html
         from pages import theme, navigation

         html.initialize(__name__)  

   3. Define a new page
         ```python
         class Index(Page):
             def  __init__(self, name):
                 self.tree = theme.base(
                     pagetitle="Sapphire Landing",
                     navigation=navigation,
                     content=[
                         h1(children=f"Welcome to {name}"),
                         p(children="{name} is a modern, open-source, and easy-to-use Content Management System (CMS) for building websites."),
                     ]
                 )

   4. Render the page on '/':
         ```python  
		 from pages.index import Index
		 index = Index("SapphireCMS") # Given this is a static page, we can use Index("SapphireCMS").prerendered() to avoid wasting resources on repeated renders. You still need to call .render() as only the tree is prerendered, not the Page object.
		 
		 router.add_route("/", "GET")(lambda  request: index.render())
 
## Serving & Sockets

### Sockets
   A simple and easy-to-use socket abstraction with HTTP and HTTPs. To be updated to support WebSockets and other socket types in the future.

### Server
   The layer that manages the sockets and workers and uses the router to route requests to the correct handler.

### Example:
   ```python
   from sapphirecms.networking import Server, Socket
   
   router = Router()
   server = Server(5, router, auto_reload=True, debug=True, secret_key=config.active.secret_key)
   
   router.add_route("/", "GET")(lambda  request: index.render())

   server.start([Socket("0.0.0.0", 80, 1024)])
   ```

## Security
   A security layer that manages the security of the website and the server.
   To be updated to support more security features in the future along with documentation.

## Storage
   A storage layer that manages the storage of the website and the server. Currently supports MongoDB.
   To be updated to support more Database Management Systems and storage types in the future along with documentation.

## Example Application:
   ```python
    from sapphirecms.routing import Router, Request
    from sapphirecms.networking import Server, Socket
    from sapphirecms import html

    html.initialize(__name__)

    router = Router()
    server = Server(5, router, auto_reload=True, debug=True, secret_key=config.active.secret_key)

    router.add_route("/", "GET")(lambda  request: "Hello, World!")

    server.start([Socket("0.0.0.0", 8080, 1024)])