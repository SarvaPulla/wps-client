from tethys_sdk.base import TethysAppBase, url_map_maker


class HydroshareWps(TethysAppBase):
    """
    Tethys app class for Hydroshare WPS.
    """

    name = 'Hydroshare WPS'
    index = 'wps:home'
    icon = 'wps/images/icon.gif'
    package = 'wps'
    root_url = 'wps'
    color = '#0099ff'
    description = 'Open a HydroShare WPS Resource Type and execute the available Web Processes through an interactive use interface.'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='wps',
                           controller='wps.controllers.home'),
                    UrlMap(name='getDescription',
                           url='wps/getDescription',
                           controller='wps.controllers.getDescription'),
                    UrlMap(name='getResults',
                           url='wps/getResults',
                           controller='wps.controllers.getResults'),
                    UrlMap(name='getXML',
                           url='wps/getXML',
                           controller='wps.controllers.getXML'),
        )

        return url_maps