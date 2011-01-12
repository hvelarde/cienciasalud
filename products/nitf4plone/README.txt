Description

    nitf4plone is a product to decorate News Items with extra
    attributes (property, section, urgency and byline) based on
    the "NITF":http://nitf.org/ specification.
    
    NITF is a XML dialect to define the content and structure of
    news articles. By using NITF, publishers can adapt the look,
    feel, and interactivity of their documents to the bandwidth,
    devices, and personalized needs of their subscribers. NITF
    was developed by the "IPTC":http://www.iptc.org/, an
    independent international association of the world's leading
    news agencies and publishers. It is a standard that is open,
    public, proven, well-used, well-documented, and
    well-supported.

    The current version supports the following attributes:

    - **property**: subject code property; includes such items
      as Analysis, Feature, and Obituary

    - **section**: named section of a publication where a news object
      appear such as Science, Sports, Weekend, etc.

    - **urgency**: 1=most, 5=normal, 8=least

    - **byline**: the real author of the news article, not just the
      person who created the item

    nitf4plone is part of the "Collective":http://dev.plone.org/collective/, so feel free to
    contribute to its development.

Acknowlegements

    This product couldn't be possible without the work of the
    following people:

    - Florian Schulze and Martin Aspeli for their archetypes.schemaextender
      product

    - Erik Rose for his Archetypes branch that enabled archetypes.schemaextender
      in Plone 2.5

Installation

    This product was tested on Plone 2.5 and Plone 3.0.

    Procedure for Plone 2.5
    
        Warning!
    
            **To use archetypes.schemaextender in Plone 2.5 you will need
            to replace Archetypes with a patched branch that will never
            be merged into the maintenance one. If you use this branch
            you are on your own in the event of a bug. Also, have in
            mind that there is no way to unregister an adapter in Zope 2.9
            (Plone 2.5), and that the adapter will be available for all
            sites in the instance.**

            **If after reading the warning you still insist on installing
            this for Plone 2.5, then use the following procedure:**
    
        First you need to replace "Archetypes":http://plone.org/products/archetypes
        with "Erik Rose's branch":http://dev.plone.org/archetypes/browser/Archetypes/branches/1.4-schemaextender-support .
    
        Now install "the latest archetypes.schemaextender":http://dev.plone.org/archetypes/browser/archetypes.schemaextender/trunk
        using normal 'python setup.py install' procedure.

        Place nitf4plone in the Products directory of your Zope
        instance and restart the server. (Linux users should fix
        permissions of files and folders first.)
    
        Go to the 'Site Setup' page in the Plone interface and click
        on the 'Add/Remove Products' link.
    
        Choose nitf4plone (check its checkbox) and click the 'Install' button.
    
        You may have to empty your browser cache to see the effects of the
        product installation/uninstallation.


    Uninstall -- **Did I warned you about
    installing this? There is no way to unregister the adapter
    so you will have to live with it or rebuild your whole Zope
    instance.**

    Procedure for Plone 3.0

        Install "the latest archetypes.schemaextender":http://dev.plone.org/archetypes/browser/archetypes.schemaextender/trunk
        using normal 'python setup.py install' procedure.
    
        Place nitf4plone in the Products directory of your Zope
        instance and restart the server. (Linux users should fix
        permissions of files and folders first.)
    
        Go to the 'Site Setup' page in the Plone interface and click
        on the 'Add/Remove Products' link.
    
        Choose nitf4plone (check its checkbox) and click the 'Install' button.
    
        You may have to empty your browser cache to see the effects of the
        product installation/uninstallation.

    Uninstall -- This can be done from the same management screen.

    Please provide feedback.

Written by

    Héctor Velarde <hvelarde@jornada.com.mx> with a little help from his friends.
