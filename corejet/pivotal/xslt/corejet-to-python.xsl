<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="text" omit-xml-declaration="yes"/>
<xsl:template match="//story">
import unittest2 as unittest
from corejet.core import Scenario, story, scenario, given, when, then


@story(id="<xsl:value-of select="@id"/>", title="<xsl:value-of select="@title"/>")
class <xsl:value-of select="translate(translate(@title,' -/&quot;', '_'), &quot;'&quot;, '')"/>(unittest.TestCase):
<xsl:for-each select="given">
    @given("<xsl:value-of select="text()"/>")
    def <xsl:value-of select="translate(translate(text(),' -/&quot;', '_'), &quot;'&quot;, '')"/>(self):
        pass
</xsl:for-each>
<xsl:for-each select="when">
    @when("<xsl:value-of select="text()"/>")
    def <xsl:value-of select="translate(translate(text(),' -/&quot;', '_'), &quot;'&quot;, '')"/>(self):
        pass
</xsl:for-each>
<xsl:for-each select="then">
    @then("<xsl:value-of select="text()"/>")
    def <xsl:value-of select="translate(translate(text(),' -/&quot;', '_'), &quot;'&quot;, '')"/>(self):
        pass
</xsl:for-each>

<xsl:apply-templates select="scenario"/>
</xsl:template>
<xsl:template match="scenario">
    @scenario("<xsl:value-of select="@name"/>")
    class <xsl:value-of select="translate(translate(@name,' -/&quot;', '_'), &quot;'&quot;, '')"/>(Scenario):
<xsl:for-each select="given">
        @given("<xsl:value-of select="text()"/>")
        def <xsl:value-of select="translate(translate(text(),' -/&quot;', '_'), &quot;'&quot;, '')"/>(self):
            pass
</xsl:for-each>
<xsl:for-each select="when">
        @when("<xsl:value-of select="text()"/>")
        def <xsl:value-of select="translate(translate(text(),' -/&quot;', '_'), &quot;'&quot;, '')"/>(self):
            pass
</xsl:for-each>
<xsl:for-each select="then">
        @then("<xsl:value-of select="text()"/>")
        def <xsl:value-of select="translate(translate(text(),' -/&quot;', '_'), &quot;'&quot;, '')"/>(self):
            pass

</xsl:for-each>
</xsl:template>
</xsl:stylesheet>