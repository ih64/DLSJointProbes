SELECT 
p.subfield, 
SUM(b.c0),
SUM(b.c1),
SUM(b.c2),
SUM(b.c3),
SUM(b.c4),
SUM(b.c5),
SUM(b.c6),
SUM(b.c7),
SUM(b.c8),
SUM(b.c9),
SUM(b.c10),
SUM(b.c11),
SUM(b.c12),
SUM(b.c13),
SUM(b.c14),
SUM(b.c15),
SUM(b.c16),
SUM(b.c17),
SUM(b.c18),
SUM(b.c19),
SUM(b.c20),
SUM(b.c21),
SUM(b.c22),
SUM(b.c23),
SUM(b.c24),
SUM(b.c25),
SUM(b.c26),
SUM(b.c27),
SUM(b.c28),
SUM(b.c29),
SUM(b.c30),
SUM(b.c31),
SUM(b.c32),
SUM(b.c33),
SUM(b.c34),
SUM(b.c35),
SUM(b.c36),
SUM(b.c37),
SUM(b.c38),
SUM(b.c39),
SUM(b.c40),
SUM(b.c41),
SUM(b.c42),
SUM(b.c43),
SUM(b.c44),
SUM(b.c45),
SUM(b.c46),
SUM(b.c47),
SUM(b.c48),
SUM(b.c49),
SUM(b.c50),
SUM(b.c51),
SUM(b.c52),
SUM(b.c53),
SUM(b.c54),
SUM(b.c55),
SUM(b.c56),
SUM(b.c57),
SUM(b.c58),
SUM(b.c59),
SUM(b.c60),
SUM(b.c61),
SUM(b.c62),
SUM(b.c63),
SUM(b.c64),
SUM(b.c65),
SUM(b.c66),
SUM(b.c67),
SUM(b.c68),
SUM(b.c69),
SUM(b.c70),
SUM(b.c71),
SUM(b.c72),
SUM(b.c73),
SUM(b.c74),
SUM(b.c75),
SUM(b.c76),
SUM(b.c77),
SUM(b.c78),
SUM(b.c79),
SUM(b.c80),
SUM(b.c81),
SUM(b.c82),
SUM(b.c83),
SUM(b.c84),
SUM(b.c85),
SUM(b.c86),
SUM(b.c87),
SUM(b.c88),
SUM(b.c89),
SUM(b.c90),
SUM(b.c91),
SUM(b.c92),
SUM(b.c93),
SUM(b.c94),
SUM(b.c95),
SUM(b.c96),
SUM(b.c97),
SUM(b.c98),
SUM(b.c99),
SUM(b.c100),
SUM(b.c101),
SUM(b.c102),
SUM(b.c103),
SUM(b.c104),
SUM(b.c105),
SUM(b.c106),
SUM(b.c107),
SUM(b.c108),
SUM(b.c109),
SUM(b.c110),
SUM(b.c111),
SUM(b.c112),
SUM(b.c113),
SUM(b.c114),
SUM(b.c115),
SUM(b.c116),
SUM(b.c117),
SUM(b.c118),
SUM(b.c119),
SUM(b.c120),
SUM(b.c121),
SUM(b.c122),
SUM(b.c123),
SUM(b.c124),
SUM(b.c125),
SUM(b.c126),
SUM(b.c127),
SUM(b.c128),
SUM(b.c129),
SUM(b.c130),
SUM(b.c131),
SUM(b.c132),
SUM(b.c133),
SUM(b.c134),
SUM(b.c135),
SUM(b.c136),
SUM(b.c137),
SUM(b.c138),
SUM(b.c139),
SUM(b.c140),
SUM(b.c141),
SUM(b.c142),
SUM(b.c143),
SUM(b.c144),
SUM(b.c145),
SUM(b.c146),
SUM(b.c147),
SUM(b.c148),
SUM(b.c149),
SUM(b.c150),
SUM(b.c151),
SUM(b.c152),
SUM(b.c153),
SUM(b.c154),
SUM(b.c155),
SUM(b.c156),
SUM(b.c157),
SUM(b.c158),
SUM(b.c159),
SUM(b.c160),
SUM(b.c161),
SUM(b.c162),
SUM(b.c163),
SUM(b.c164),
SUM(b.c165),
SUM(b.c166),
SUM(b.c167),
SUM(b.c168),
SUM(b.c169),
SUM(b.c170),
SUM(b.c171),
SUM(b.c172),
SUM(b.c173),
SUM(b.c174),
SUM(b.c175),
SUM(b.c176),
SUM(b.c177),
SUM(b.c178),
SUM(b.c179),
SUM(b.c180),
SUM(b.c181),
SUM(b.c182),
SUM(b.c183),
SUM(b.c184),
SUM(b.c185),
SUM(b.c186),
SUM(b.c187),
SUM(b.c188),
SUM(b.c189),
SUM(b.c190),
SUM(b.c191),
SUM(b.c192),
SUM(b.c193),
SUM(b.c194),
SUM(b.c195),
SUM(b.c196),
SUM(b.c197),
SUM(b.c198),
SUM(b.c199),
SUM(b.c200)
FROM
RC1Stage.PhotoObjAll AS p, 
RC1c_public.Dlsqc AS d, 
RC1c_public.Bpz AS z, 
RC1Stage.Shapes2 AS s,
RC1c_public.Probs as b 
WHERE
d.objid=s.objid
AND p.objid = s.objid
AND p.objid = z.objid
AND z.objid = b.objid
AND p.objid IS NOT NULL
AND p.processflags<8
AND p.r is NOT NULL
AND p.b is NOT NULL
AND p.v is NOT NULL
AND p.z is NOT NULL
AND p.r < 24.5
AND p.r > 21
# The R band probability that object is a point source `d.Dlsqc_prob`
AND d.Dlsqc_prob<0.1
# Shape cut
AND s.b>0.1
AND z.z_b < .9
AND z.z_b>0.7
# Ellipticity error cut
AND s.de<0.25
# F5 bound cut F5 is a 2x2 sq. degree field centered at RA=13:59:20, DEC=-11:03:00
# Due to ambiguous info on DLS website and James 2015 cosmic shear paper about the location
# of the field I will use the SQL keyword instead
# AND p.alpha between 208.7 and 210.85
# AND p.delta between -12.1 and -10.1;
#AND p.subfield LIKE 'F2%'
GROUP BY p.subfield 